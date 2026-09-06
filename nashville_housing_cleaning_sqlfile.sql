/* ============================================================================
   NASHVILLE HOUSING DATA -- DATA CLEANING SQL SCRIPT
   ============================================================================
   Source file : Nashville_Housing_Data_for_Data_Cleaning.csv (56,477 rows)
   Engine used : SQLite 3.45 (chosen for a fully self-contained, portable
                 pipeline). Syntax is close to ANSI SQL; PostgreSQL / SQL
                 Server equivalents are noted in comments where the syntax
                 genuinely differs, since most warehouses would use one of
                 those in production.
   Author      : Claude (Anthropic), Data Cleaning Pipeline
   ----------------------------------------------------------------------------
   PIPELINE OVERVIEW
     0. Load the raw CSV into a TEXT-only staging table (housing_raw), exactly
        as a bulk CSV import would land it -- no assumptions about types yet.
     1. Create housing_cleaned with proper column types and load it from the
        staging table, applying casting, trimming, date-parsing, and category
        standardization in a single pass.
     2. Recover missing PropertyAddress values from matching ParcelIDs.
     3. Split combined address fields into their components.
     4. Remove duplicate transactions.
     5. Add derived analytical columns used later for trend analysis.
     6. (Optional / commented out) Drop the now-redundant raw address columns,
        for anyone who wants the leaner schema used in the classic version of
        this exercise. Left in place by default -- see the note in Section 6.
   ============================================================================ */


/* ----------------------------------------------------------------------------
   SECTION 0: STAGING TABLE
   The raw CSV is loaded into housing_raw with every column as TEXT, mirroring
   a naive bulk import. All parsing/casting below is explicit and visible,
   rather than relying on the CSV loader to guess types.
   (Populated by the pipeline's ETL step, e.g. `.import` / driver bulk-load;
   not reproduced here since it is driver-specific.)
---------------------------------------------------------------------------- */
-- CREATE TABLE housing_raw (UniqueID TEXT, ParcelID TEXT, LandUse TEXT,
--     PropertyAddress TEXT, SaleDate TEXT, SalePrice TEXT, LegalReference TEXT,
--     SoldAsVacant TEXT, OwnerName TEXT, OwnerAddress TEXT, Acreage TEXT,
--     TaxDistrict TEXT, LandValue TEXT, BuildingValue TEXT, TotalValue TEXT,
--     YearBuilt TEXT, Bedrooms TEXT, FullBath TEXT, HalfBath TEXT);


/* ----------------------------------------------------------------------------
   SECTION 1: BUILD THE CLEANED TABLE WITH PROPER TYPES
---------------------------------------------------------------------------- */
DROP TABLE IF EXISTS housing_cleaned;

CREATE TABLE housing_cleaned (
    UniqueID              INTEGER PRIMARY KEY,
    ParcelID              TEXT,
    LandUse               TEXT,
    LandUseStandardized   TEXT,
    PropertyAddress       TEXT,
    SaleDate              TEXT,      -- ISO 8601: YYYY-MM-DD
    SaleYear              INTEGER,
    SaleMonth             INTEGER,
    SalePrice             INTEGER,
    LegalReference        TEXT,
    SoldAsVacant          TEXT,
    OwnerName             TEXT,
    OwnerAddress          TEXT,
    Acreage               REAL,
    TaxDistrict           TEXT,
    LandValue             INTEGER,
    BuildingValue         INTEGER,
    TotalValue            INTEGER,
    YearBuilt             INTEGER,
    Bedrooms              INTEGER,
    FullBath              INTEGER,
    HalfBath              INTEGER
);

INSERT INTO housing_cleaned (
    UniqueID, ParcelID, LandUse, LandUseStandardized, PropertyAddress,
    SaleDate, SaleYear, SaleMonth, SalePrice, LegalReference, SoldAsVacant,
    OwnerName, OwnerAddress, Acreage, TaxDistrict, LandValue, BuildingValue,
    TotalValue, YearBuilt, Bedrooms, FullBath, HalfBath
)
SELECT
    CAST(TRIM(UniqueID) AS INTEGER),
    TRIM(ParcelID),
    TRIM(LandUse),

    -- Standardize near-duplicate / corrupted LandUse category labels into a
    -- clean dimension while leaving the original LandUse value untouched for
    -- audit purposes:
    --   * "VACANT RES LAND" and the typo "VACANT RESIENTIAL LAND" both really
    --     mean "VACANT RESIDENTIAL LAND" (1,552 rows affected)
    --   * One category was corrupted with an embedded line break and a
    --     mis-typed duplicate value: "GREENBELT/RES\r\nGRRENBELT/RES"
    --     (3 rows) -> "GREENBELT/RES"
    CASE
        WHEN TRIM(LandUse) LIKE 'GREENBELT/RES%' THEN 'GREENBELT/RES'
        WHEN TRIM(LandUse) IN ('VACANT RES LAND', 'VACANT RESIENTIAL LAND')
            THEN 'VACANT RESIDENTIAL LAND'
        ELSE TRIM(LandUse)
    END,

    -- Collapse repeated internal whitespace in PropertyAddress. The source
    -- system embeds a double space either after the house number or before
    -- the street suffix inconsistently (e.g. "1808  FOX CHASE DR" vs.
    -- "1808 FOX CHASE  DR" for the SAME address), which otherwise causes
    -- identical addresses to look different in later joins/dedup checks.
    TRIM(REPLACE(REPLACE(REPLACE(PropertyAddress, '  ', ' '), '  ', ' '), '  ', ' ')),

    -- Parse "Month D, YYYY" (e.g. "April 9, 2013") into ISO 8601 date text.
    -- PostgreSQL equivalent:  TO_DATE(SaleDate, 'FMMonth DD, YYYY')
    -- SQL Server equivalent:  CONVERT(date, SaleDate, 107)
    CASE WHEN SaleDate IS NULL THEN NULL ELSE
        SUBSTR(SaleDate, -4) || '-' ||
        CASE SUBSTR(SaleDate, 1, INSTR(SaleDate, ' ') - 1)
            WHEN 'January'   THEN '01' WHEN 'February' THEN '02' WHEN 'March'     THEN '03'
            WHEN 'April'     THEN '04' WHEN 'May'      THEN '05' WHEN 'June'      THEN '06'
            WHEN 'July'      THEN '07' WHEN 'August'   THEN '08' WHEN 'September' THEN '09'
            WHEN 'October'   THEN '10' WHEN 'November' THEN '11' WHEN 'December'  THEN '12'
        END || '-' ||
        PRINTF('%02d', CAST(TRIM(SUBSTR(SaleDate, INSTR(SaleDate, ' ') + 1,
            INSTR(SaleDate, ',') - INSTR(SaleDate, ' ') - 1)) AS INTEGER))
    END,

    -- SaleYear / SaleMonth, derived up front for trend analysis (avoids
    -- repeated date parsing in every downstream query).
    CAST(SUBSTR(SaleDate, -4) AS INTEGER),
    CASE SUBSTR(SaleDate, 1, INSTR(SaleDate, ' ') - 1)
        WHEN 'January'   THEN 1 WHEN 'February' THEN 2 WHEN 'March'     THEN 3
        WHEN 'April'     THEN 4 WHEN 'May'      THEN 5 WHEN 'June'      THEN 6
        WHEN 'July'      THEN 7 WHEN 'August'   THEN 8 WHEN 'September' THEN 9
        WHEN 'October'   THEN 10 WHEN 'November' THEN 11 WHEN 'December' THEN 12
    END,

    CAST(REPLACE(REPLACE(TRIM(SalePrice), ',', ''), '$', '') AS INTEGER),
    TRIM(LegalReference),

    -- Standardize "Sold As Vacant": Y/N -> Yes/No (451 rows used the Y/N
    -- shorthand while the rest of the column used Yes/No).
    CASE TRIM(SoldAsVacant)
        WHEN 'Y' THEN 'Yes'
        WHEN 'N' THEN 'No'
        ELSE TRIM(SoldAsVacant)
    END,

    NULLIF(TRIM(OwnerName), ''),
    NULLIF(TRIM(REPLACE(REPLACE(REPLACE(OwnerAddress, '  ', ' '), '  ', ' '), '  ', ' ')), ''),
    CAST(Acreage AS REAL),
    NULLIF(TRIM(TaxDistrict), ''),
    CAST(LandValue AS INTEGER),
    CAST(BuildingValue AS INTEGER),
    CAST(TotalValue AS INTEGER),
    CAST(YearBuilt AS INTEGER),
    CAST(Bedrooms AS INTEGER),
    CAST(FullBath AS INTEGER),
    CAST(HalfBath AS INTEGER)
FROM housing_raw;


/* ----------------------------------------------------------------------------
   SECTION 2: POPULATE MISSING PROPERTY ADDRESS
   29 rows had a NULL PropertyAddress. Every ParcelID is a physical parcel of
   land, so if ANY other row sharing the same ParcelID has a known address,
   that address applies here too. Self-join on ParcelID, excluding the row
   itself, and backfill.
---------------------------------------------------------------------------- */
UPDATE housing_cleaned
SET PropertyAddress = (
    SELECT b.PropertyAddress
    FROM housing_cleaned b
    WHERE b.ParcelID = housing_cleaned.ParcelID
      AND b.UniqueID != housing_cleaned.UniqueID
      AND b.PropertyAddress IS NOT NULL
    LIMIT 1
)
WHERE PropertyAddress IS NULL;
-- Result: all 29 missing addresses recovered (0 remain NULL).


/* ----------------------------------------------------------------------------
   SECTION 3: SPLIT ADDRESS FIELDS INTO COMPONENTS
   Verified before writing this: PropertyAddress always contains exactly one
   comma ("<street address>, <city>"), and OwnerAddress always contains
   exactly two ("<street address>, <city>, <state>") in every non-null value.
   That makes position-based splitting reliable here.
   PostgreSQL equivalent: SPLIT_PART(column, ',', n)
---------------------------------------------------------------------------- */
ALTER TABLE housing_cleaned ADD COLUMN PropertySplitAddress TEXT;
ALTER TABLE housing_cleaned ADD COLUMN PropertySplitCity    TEXT;
ALTER TABLE housing_cleaned ADD COLUMN OwnerSplitAddress    TEXT;
ALTER TABLE housing_cleaned ADD COLUMN OwnerSplitCity       TEXT;
ALTER TABLE housing_cleaned ADD COLUMN OwnerSplitState      TEXT;

UPDATE housing_cleaned
SET PropertySplitAddress = TRIM(SUBSTR(PropertyAddress, 1, INSTR(PropertyAddress, ',') - 1)),
    PropertySplitCity    = TRIM(SUBSTR(PropertyAddress, INSTR(PropertyAddress, ',') + 1));

UPDATE housing_cleaned
SET OwnerSplitAddress = TRIM(SUBSTR(OwnerAddress, 1, INSTR(OwnerAddress, ',') - 1)),
    OwnerSplitCity     = TRIM(SUBSTR(
                             SUBSTR(OwnerAddress, INSTR(OwnerAddress, ',') + 1), 1,
                             INSTR(SUBSTR(OwnerAddress, INSTR(OwnerAddress, ',') + 1), ',') - 1
                         )),
    OwnerSplitState    = TRIM(SUBSTR(
                             SUBSTR(OwnerAddress, INSTR(OwnerAddress, ',') + 1),
                             INSTR(SUBSTR(OwnerAddress, INSTR(OwnerAddress, ',') + 1), ',') + 1
                         ))
WHERE OwnerAddress IS NOT NULL;


/* ----------------------------------------------------------------------------
   SECTION 4: REMOVE DUPLICATE TRANSACTIONS
   A true duplicate here is the same parcel, address, price, sale date, and
   legal (deed) reference appearing more than once -- i.e. the same recorded
   transaction inserted twice under a different UniqueID.
   IMPORTANT: this runs AFTER Sections 2-3 on purpose. One duplicate pair
   (UniqueID 27140) had a blank PropertyAddress in the raw file, so a naive
   dedup on the untouched raw data would have missed it. Filling addresses
   first raised the true duplicate count from 103 to 104.
---------------------------------------------------------------------------- */
DELETE FROM housing_cleaned
WHERE UniqueID IN (
    SELECT UniqueID FROM (
        SELECT
            UniqueID,
            ROW_NUMBER() OVER (
                PARTITION BY ParcelID, PropertyAddress, SalePrice, SaleDate, LegalReference
                ORDER BY UniqueID
            ) AS rn
        FROM housing_cleaned
    )
    WHERE rn > 1
);
-- Result: 104 duplicate rows removed. 56,477 -> 56,373 rows.


/* ----------------------------------------------------------------------------
   SECTION 5: DERIVED ANALYTICAL COLUMNS
---------------------------------------------------------------------------- */
ALTER TABLE housing_cleaned ADD COLUMN HouseAge               INTEGER;
ALTER TABLE housing_cleaned ADD COLUMN TotalBathrooms         REAL;
ALTER TABLE housing_cleaned ADD COLUMN PricePerAcre           REAL;
ALTER TABLE housing_cleaned ADD COLUMN LegalRefRecordingDate  TEXT;
ALTER TABLE housing_cleaned ADD COLUMN SaleLegalDateDiffDays  INTEGER;

-- Age of the structure at the time of sale.
UPDATE housing_cleaned SET HouseAge = SaleYear - YearBuilt WHERE YearBuilt IS NOT NULL;

-- Bathroom count expressed as a single comparable number.
UPDATE housing_cleaned
SET TotalBathrooms = COALESCE(FullBath, 0) + 0.5 * COALESCE(HalfBath, 0)
WHERE FullBath IS NOT NULL OR HalfBath IS NOT NULL;

-- Normalized value metric for comparing parcels of different sizes.
UPDATE housing_cleaned
SET PricePerAcre = ROUND(SalePrice / Acreage, 2)
WHERE Acreage IS NOT NULL AND Acreage > 0;

-- QA CHECK (informational only -- does not alter SaleDate or LegalReference):
-- LegalReference embeds its own recording date as its first 8 characters
-- (YYYYMMDD). Cross-checking it against SaleDate surfaces likely data-entry
-- errors, e.g. two rows recorded a SaleDate of 2019 while their
-- LegalReference clearly points to a 2014/2016 recording.
UPDATE housing_cleaned
SET LegalRefRecordingDate =
    SUBSTR(LegalReference,1,4) || '-' || SUBSTR(LegalReference,5,2) || '-' || SUBSTR(LegalReference,7,2)
WHERE LENGTH(LegalReference) >= 8;

UPDATE housing_cleaned
SET SaleLegalDateDiffDays = CAST(JULIANDAY(SaleDate) - JULIANDAY(LegalRefRecordingDate) AS INTEGER)
WHERE LegalRefRecordingDate IS NOT NULL AND JULIANDAY(LegalRefRecordingDate) IS NOT NULL;
-- 17 rows differ by more than 365 days -- flagged in the cleaning log for
-- manual review, not auto-corrected (we should not guess-edit a legal
-- deed reference or an official sale date).

-- QA CHECK (informational only): flag bulk / multi-parcel transactions.
-- Some transactions cover many parcels at once (a developer selling an
-- entire subdivision phase, or a portfolio/bulk condo sale), and the source
-- data records the SAME full transaction price against EVERY individual
-- parcel involved, rather than an allocated per-parcel price. Example: 92
-- separate lots on Lincoya Creek Dr all show SalePrice = $13,156,000 for the
-- same SaleDate/LegalReference -- that is one $13.156M transaction, not 92.
-- This column counts how many distinct parcels share the same
-- (SalePrice, SaleDate, LegalReference); a value of 1 is a normal
-- single-parcel sale, >1 flags a bulk transaction. See the cleaning log for
-- the sizable effect this has on any "total sales volume" figure.
CREATE INDEX IF NOT EXISTS idx_bulk_key ON housing_cleaned (SalePrice, SaleDate, LegalReference);

ALTER TABLE housing_cleaned ADD COLUMN BulkTransactionParcelCount INTEGER;

UPDATE housing_cleaned
SET BulkTransactionParcelCount = (
    SELECT COUNT(DISTINCT b.ParcelID)
    FROM housing_cleaned b
    WHERE b.SalePrice = housing_cleaned.SalePrice
      AND b.SaleDate = housing_cleaned.SaleDate
      AND b.LegalReference = housing_cleaned.LegalReference
);


/* ----------------------------------------------------------------------------
   SECTION 6 (OPTIONAL, NOT APPLIED): DROP REDUNDANT RAW COLUMNS
   The classic version of this exercise drops OwnerAddress, TaxDistrict, and
   the original PropertyAddress once split. We deliberately did NOT do this
   in the delivered dataset -- keeping the original columns preserves an
   audit trail and costs nothing. If you want the leaner schema, run:

   ALTER TABLE housing_cleaned DROP COLUMN OwnerAddress;
   ALTER TABLE housing_cleaned DROP COLUMN TaxDistrict;
   ALTER TABLE housing_cleaned DROP COLUMN PropertyAddress;
---------------------------------------------------------------------------- */


/* ----------------------------------------------------------------------------
   SECTION 7: FINAL VALIDATION QUERIES
---------------------------------------------------------------------------- */
-- SELECT COUNT(*) FROM housing_cleaned;                                  -- 56,373
-- SELECT COUNT(*) FROM housing_cleaned WHERE PropertyAddress IS NULL;    -- 0
-- SELECT COUNT(DISTINCT UniqueID) FROM housing_cleaned;                  -- 56,373 (matches row count)
-- SELECT ParcelID, PropertyAddress, SalePrice, SaleDate, LegalReference, COUNT(*)
--   FROM housing_cleaned GROUP BY 1,2,3,4,5 HAVING COUNT(*) > 1;         -- 0 rows (no dupes remain)
-- SELECT SUM(SalePrice) FROM housing_cleaned WHERE BulkTransactionParcelCount = 1;
--   -- "clean" single-parcel-only sales volume, with bulk transactions excluded entirely
