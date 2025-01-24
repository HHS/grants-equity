import { FilterOption } from "src/components/search/SearchFilterAccordion/SearchFilterAccordion";

export const eligibilityOptions: FilterOption[] = [
  {
    id: "eligibility-state_governments",
    label: "State Governments",
    value: "state_governments",
  },
  {
    id: "eligibility-county_governments",
    label: "County Governments",
    value: "county_governments",
  },
  {
    id: "eligibility-city_or_township_governments",
    label: "City or Township Governments",
    value: "city_or_township_governments",
  },
  {
    id: "eligibility-special_district_governments",
    label: "Special District Governments",
    value: "special_district_governments",
  },
  {
    id: "eligibility-independent_school_districts",
    label: "Independent School Districts",
    value: "independent_school_districts",
  },
  {
    id: "eligibility-public_and_state_institutions_of_higher_education",
    label: "Public and State Institutions of Higher Education",
    value: "public_and_state_institutions_of_higher_education",
  },
  {
    id: "eligibility-private_institutions_of_higher_education",
    label: "Private Institutions of Higher Education",
    value: "private_institutions_of_higher_education",
  },
  {
    id: "eligibility-federally_recognized_native_american_tribal_governments",
    label: "Federally Recognized Native American Tribal Governments",
    value: "federally_recognized_native_american_tribal_governments",
  },
  {
    id: "eligibility-other_native_american_tribal_organizations",
    label: "Other Native American Tribal Organizations",
    value: "other_native_american_tribal_organizations",
  },
  {
    id: "eligibility-public_and_indian_housing_authorities",
    label: "Public and Indian Housing Authorities",
    value: "public_and_indian_housing_authorities",
  },
  {
    id: "eligibility-nonprofits_non_higher_education_with_501c3",
    label:
      "Nonprofits without 501(c)(3), other than institutions of higher education",
    value: "nonprofits_non_higher_education_with_501c3",
  },
  {
    id: "eligibility-nonprofits_non_higher_education_without_501c3",
    label:
      "Nonprofits with 501(c)(3), other than institutions of higher education",
    value: "nonprofits_non_higher_education_without_501c3",
  },
  {
    id: "eligibility-individuals",
    label: "Individuals",
    value: "individuals",
  },
  {
    id: "eligibility-for_profit_organizations_other_than_small_businesses",
    label: "For-Profit Organizations Other Than Small Businesses",
    value: "for_profit_organizations_other_than_small_businesses",
  },
  {
    id: "eligibility-small_businesses",
    label: "Small Businesses",
    value: "small_businesses",
  },
  {
    id: "eligibility-other",
    label: "Other",
    value: "other",
  },
  {
    id: "eligibility-unrestricted",
    label: "Unrestricted",
    value: "unrestricted",
  },
];

export const fundingOptions: FilterOption[] = [
  {
    id: "funding-instrument-cooperative_agreement",
    label: "Cooperative Agreement",
    value: "cooperative_agreement",
  },
  {
    id: "funding-instrument-grant",
    label: "Grant",
    value: "grant",
  },
  {
    id: "funding-instrument-procurement_contract",
    label: "Procurement Contract ",
    value: "procurement_contract",
  },
  {
    id: "funding-instrument-other",
    label: "Other",
    value: "other",
  },
];

export const categoryOptions: FilterOption[] = [
  {
    id: "category-recovery_act",
    label: "Recovery Act",
    value: "recovery_act",
  },
  { id: "category-agriculture", label: "Agriculture", value: "agriculture" },
  { id: "category-arts", label: "Arts", value: "arts" },
  {
    id: "category-business_and_commerce",
    label: "Business and Commerce",
    value: "business_and_commerce",
  },
  {
    id: "category-community_development",
    label: "Community Development",
    value: "community_development",
  },
  {
    id: "category-consumer_protection",
    label: "Consumer Protection",
    value: "consumer_protection",
  },
  {
    id: "category-disaster_prevention_and_relief",
    label: "Disaster Prevention and Relief",
    value: "disaster_prevention_and_relief",
  },
  { id: "category-education", label: "Education", value: "education" },
  {
    id: "category-employment_labor_and_training",
    label: "Employment, Labor, and Training",
    value: "employment_labor_and_training",
  },
  { id: "category-energy", label: "Energy", value: "energy" },
  { id: "category-environment", label: "Environment", value: "environment" },
  {
    id: "category-food_and_nutrition",
    label: "Food and Nutrition",
    value: "food_and_nutrition",
  },
  { id: "category-health", label: "Health", value: "health" },
  { id: "category-housing", label: "Housing", value: "housing" },
  { id: "category-humanities", label: "Humanities", value: "humanities" },
  {
    id: "category-information_and_statistics",
    label: "Information and Statistics",
    value: "information_and_statistics",
  },
  {
    id: "category-infrastructure_investment_and_jobs_act",
    label: "Infrastructure Investment and Jobs Act",
    value: "infrastructure_investment_and_jobs_act",
  },
  {
    id: "category-income_security_and_social_services",
    label: "Income Security and Social Services",
    value: "income_security_and_social_services",
  },
  {
    id: "category-law_justice_and_legal_services",
    label: "Law, Justice, and Legal Services",
    value: "law_justice_and_legal_services",
  },
  {
    id: "category-natural_resources",
    label: "Natural Resources",
    value: "natural_resources",
  },
  {
    id: "category-opportunity_zone_benefits",
    label: "Opportunity Zone Benefits",
    value: "opportunity_zone_benefits",
  },
  {
    id: "category-regional_development",
    label: "Regional Development",
    value: "regional_development",
  },
  {
    id: "category-science_technology_and_other_research_and_development",
    label: "Science, Technology, and Other Research and Development",
    value: "science_technology_and_other_research_and_development",
  },
  {
    id: "category-transportation",
    label: "Transportation",
    value: "transportation",
  },
  {
    id: "category-affordable_care_act",
    label: "Affordable Care Act",
    value: "affordable_care_act",
  },
  { id: "category-other", label: "Other", value: "other" },
];
