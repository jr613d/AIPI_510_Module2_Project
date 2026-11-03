"""Shared input paths for the intersections workstreams. Read-only inputs live in the
Module 1 and Module 2 projects; nothing here writes to them."""
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent                          # exploratory_analysis/07_intersections_FABLE/
RESULTS = ROOT / "results"
PROCESSED = ROOT / "data" / "processed"

SOURCING = ROOT.parents[3]                  # 510_Sourcing_Data/ (ROOT -> exploratory_analysis -> repo -> Module_2_Project -> here)
M1 = SOURCING / "Module_1_Project" / "CHCCS Enrollment Decline Deep Dive"
M1_FABLE = M1 / "interactive_visualizations_FABLE"
ASTRA = SOURCING / "Module_1_Project" / "ASTRA" / "school-map"
M2 = SOURCING / "Module_2_Project" / "AIPI_510_Module2_Project"
M2_EXPL = M2 / "exploratory_analysis"

# Module 2 (survey)
RESPONSES_WIDE = M2_EXPL / "data" / "processed" / "responses_wide.csv"      # one row per response, all ratings + text + group + q9 theme
Q1_ROLES = M2 / "data" / "processed" / "chccs_respondent_relationships.csv"  # one-hot Q1 roles
Q9_THEMES = M2 / "data" / "processed" / "q9_value_themes.csv"
BOARD_VS_CPA = M2_EXPL / "data" / "raw" / "full_report_board_vs_cpa_transcribed.csv"
WRITE_IN_CODES = M2_EXPL / "04_write_ins" / "results" / "write_in_codes_by_response.csv"
RAW_WORKBOOK = M2 / "data" / "raw" / "CHCCS Community Priorities Asessment (SHARED).xlsx"

# Module 1 (DPI enrollment, population, alternatives)
CHCCS_LAYERS = M1 / "data" / "cleaned" / "chccs_layers.csv"                 # 2019-2024 four nested layers + capture rate
SCHOOL_ADM = M1 / "data" / "cleaned" / "school_adm_with_spans.csv"           # school x year ADM, all NC
ELEM_CHANGE = M1 / "data" / "cleaned" / "elementary_change_by_district.csv"
LEA_POP = M1_FABLE / "data" / "cleaned" / "population_lea_long.csv"         # SAIPE by LEA, 2005-2024 (pop_total, pop_5_17, pov_5_17)
COUNTY_POP = M1_FABLE / "data" / "cleaned" / "population_county_long.csv"
COUNTY_ADM = M1_FABLE / "data" / "cleaned" / "county_adm_wide.csv"           # lea_/charter_/total_ by county by year
CHARTER_BY_COUNTY = M1_FABLE / "data" / "cleaned" / "charter_adm_by_county_wide.csv"
NONPUBLIC = M1_FABLE / "data" / "cleaned" / "nonpublic_by_county_long.csv"  # DNPE private + home by county
VOUCHERS = M1_FABLE / "data" / "cleaned" / "vouchers_prior_lea_long.csv"
SCHOOL_OPTIONS = M1_FABLE / "data" / "cleaned" / "school_options.csv"        # charter/private alternatives near CHCCS
PODCAST_DATA = M1_FABLE / "data" / "cleaned" / "podcast_data.json"           # chccsSchools, orangeAges, board forecasts
BOARD_FORECAST = M1_FABLE / "data" / "raw" / "chccs_board" / "board_deck_district_adm_projection.csv"
CLOSURE_FORECAST = M1_FABLE / "data" / "raw" / "chccs_board" / "closure_study_elementary_forecast_2026-2036.csv"
CENSUS_AGESEX_2024 = M1_FABLE / "data" / "raw" / "census_popest" / "cc-est2024-agesex-37.csv"
CENSUS_AGESEX_2019 = M1_FABLE / "data" / "raw" / "census_popest" / "cc-est2019-agesex-37.csv"
DPI_EDS = M1 / "data_sources" / "nc_dpi_rcd_acc_eds_2024-25.csv"            # % economically disadvantaged, school + LEA level
DPI_CHRONIC = M1 / "data_sources" / "nc_dpi_rcd_chronic_absent_2024-25.csv"
DPI_LOCATION = M1 / "data_sources" / "nc_dpi_rcd_location_2024-25.csv"
DPI_FUNDS = M1 / "data_sources" / "nc_dpi_rcd_funds2_2024-25.csv"
SPG_XLSX = SOURCING / "Module_2_Project" / "archive" / "school_grades_enrollment" / "data" / "raw" / "rcd_acc_spg2.xlsx"

# ASTRA atlas (school zones, walk flags, capacity, home values)
SCHOOL_METRICS = ASTRA / "data" / "school_metrics.csv"                       # ADM, SAPFO capacity, utilization, 2026 program capacity, 2031 forecast util
CAPACITY_SOURCES = ASTRA / "data" / "school_capacity_sources.json"
MAP_DATA = ASTRA / "data" / "map_data.json"                                  # segments (ESWALK flags), boundaries, schools, housing block groups
SEGMENTS_GEOJSON = ASTRA / "data" / "segments.geojson"
HOUSING_GEOJSON = ASTRA / "data" / "housing_blockgroups_raw.geojson"
ACS_B25077 = ASTRA / "data" / "acs2024_b25077_extract.csv"                   # median owner-occupied home value by block group
ACS_B25003 = ASTRA / "data" / "acs2024_b25003_extract.csv"                   # tenure (owner/renter) by block group
CLOSURE_STUDY_TXT = ASTRA / "research" / "closure_study_2026-05-07.txt"
BOARD_DECK_TXT = ASTRA / "research" / "board_retreat_deck_2025-12-11.txt"

CHCCS_LEA = "681LEA"
ELEM_CODES = {  # DPI school code -> name (11 elementary schools)
    "681300": "Northside", "681304": "Carrboro", "681310": "Seawell", "681311": "Ephesus",
    "681312": "Estes Hills", "681316": "Frank Porter Graham", "681320": "Glenwood",
    "681326": "McDougle", "681330": "Scroggs", "681332": "Morris Grove", "681334": "Rashkis",
}
CLOSURE_CANDIDATES = {"Ephesus", "Glenwood", "Seawell"}
DLI_SCHOOLS = {"Carrboro": "Spanish DLI", "Frank Porter Graham": "Spanish DLI (Bilingüe magnet)", "Glenwood": "Mandarin DLI (lottery magnet)"}
