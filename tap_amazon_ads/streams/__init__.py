from tap_amazon_ads.streams.profiles import Profiles
from tap_amazon_ads.streams.portfolios import Portfolios
from tap_amazon_ads.streams.sponsored_display_campaigns import SponsoredDisplayCampaigns
from tap_amazon_ads.streams.sponsored_display_ad_groups import SponsoredDisplayAdGroups
from tap_amazon_ads.streams.sponsored_display_product_ads import SponsoredDisplayProductAds
from tap_amazon_ads.streams.sponsored_display_targetings import SponsoredDisplayTargetings
from tap_amazon_ads.streams.sponsored_display_budget_rules import SponsoredDisplayBudgetRules
from tap_amazon_ads.streams.sponsored_display_brand_safety_list import SponsoredDisplayBrandSafetyList
from tap_amazon_ads.streams.sponsored_display_negative_targeting_clauses import SponsoredDisplayNegativeTargetingClauses
from tap_amazon_ads.streams.sponsored_display_creatives import SponsoredDisplayCreatives
from tap_amazon_ads.streams.sponsored_brands_campaigns import SponsoredBrandsCampaigns
from tap_amazon_ads.streams.sponsored_brands_ad_groups import SponsoredBrandsAdGroups
from tap_amazon_ads.streams.sponsored_brands_keywords import SponsoredBrandsKeywords
from tap_amazon_ads.streams.sponsored_brands_negative_keywords import SponsoredBrandsNegativeKeywords
from tap_amazon_ads.streams.sponsored_brands_bid_recommendations import SponsoredBrandsBidRecommendations
from tap_amazon_ads.streams.sponsored_brands_negative_targets import SponsoredBrandsNegativeTargets
from tap_amazon_ads.streams.sponsored_brands_product_targets import SponsoredBrandsProductTargets
from tap_amazon_ads.streams.sponsored_brands_store_assets import SponsoredBrandsStoreAssets
from tap_amazon_ads.streams.sponsored_brands_ad_creatives import SponsoredBrandsAdCreatives
from tap_amazon_ads.streams.sponsored_brands_budget_rules import SponsoredBrandsBudgetRules
from tap_amazon_ads.streams.sponsored_products_campaigns import SponsoredProductsCampaigns
from tap_amazon_ads.streams.sponsored_products_ad_groups import SponsoredProductsAdGroups
from tap_amazon_ads.streams.sponsored_products_keywords import SponsoredProductsKeywords
from tap_amazon_ads.streams.sponsored_products_negative_keywords import SponsoredProductsNegativeKeywords
from tap_amazon_ads.streams.sponsored_products_ads import SponsoredProductsAds
from tap_amazon_ads.streams.sponsored_products_budget_rules import SponsoredProductsBudgetRules
from tap_amazon_ads.streams.invoices import Invoices

STREAMS = {
    "profiles": Profiles,
    "portfolios": Portfolios,
    "sponsored_display_campaigns": SponsoredDisplayCampaigns,
    "sponsored_display_ad_groups": SponsoredDisplayAdGroups,
    "sponsored_display_product_ads": SponsoredDisplayProductAds,
    "sponsored_display_targetings": SponsoredDisplayTargetings,
    "sponsored_display_budget_rules": SponsoredDisplayBudgetRules,
    "sponsored_display_brand_safety_list": SponsoredDisplayBrandSafetyList,
    "sponsored_display_negative_targeting_clauses": SponsoredDisplayNegativeTargetingClauses,
    "sponsored_display_creatives": SponsoredDisplayCreatives,
    "sponsored_brands_campaigns": SponsoredBrandsCampaigns,
    "sponsored_brands_ad_groups": SponsoredBrandsAdGroups,
    "sponsored_brands_keywords": SponsoredBrandsKeywords,
    "sponsored_brands_negative_keywords": SponsoredBrandsNegativeKeywords,
    "sponsored_brands_bid_recommendations": SponsoredBrandsBidRecommendations,
    "sponsored_brands_negative_targets": SponsoredBrandsNegativeTargets,
    "sponsored_brands_product_targets": SponsoredBrandsProductTargets,
    "sponsored_brands_store_assets": SponsoredBrandsStoreAssets,
    "sponsored_brands_ad_creatives": SponsoredBrandsAdCreatives,
    "sponsored_brands_budget_rules": SponsoredBrandsBudgetRules,
    "sponsored_products_campaigns": SponsoredProductsCampaigns,
    "sponsored_products_ad_groups": SponsoredProductsAdGroups,
    "sponsored_products_keywords": SponsoredProductsKeywords,
    "sponsored_products_negative_keywords": SponsoredProductsNegativeKeywords,
    "sponsored_products_ads": SponsoredProductsAds,
    "sponsored_products_budget_rules": SponsoredProductsBudgetRules,
    "invoices": Invoices,
}
