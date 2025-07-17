# tap-amazon_ads

This is a [Singer](https://singer.io) tap that produces JSON-formatted data
following the [Singer
spec](https://github.com/singer-io/getting-started/blob/master/docs/SPEC.md).

This tap:

- Pulls raw data from the [Amazon_Ads API].
- Extracts the following resources:
    - [Invoices](https://advertising.amazon.com/API/docs/en-us/billing#tag/invoice/operation/getAdvertiserInvoices)

    - [Portfolios](https://advertising.amazon.com/API/docs/en-us/reference/portfolios#tag/Portfolios/operation/ListPortfolios)

    - [Profiles](https://advertising.amazon.com/API/docs/en-us/reference/2/profiles#tag/Profiles/operation/listProfiles)

    - [SponsoredBrandsAdCreatives](https://advertising.amazon.com/API/docs/en-us/sponsored-brands/3-0/openapi/prod#tag/Ad-creatives/operation/ListCreatives)

    - [SponsoredBrandsAdGroups](https://advertising.amazon.com/API/docs/en-us/sponsored-brands/3-0/openapi/prod#tag/Ad-groups/operation/ListSponsoredBrandsAdGroups)

    - [SponsoredBrandsAds](https://advertising.amazon.com/API/docs/en-us/sponsored-brands/3-0/openapi/prod#tag/Ads/operation/ListSponsoredBrandsAds)

    - [SponsoredBrandsBidRecommendations](https://advertising.amazon.com/API/docs/en-us/sponsored-brands/3-0/openapi#tag/Bid-recommendations/operation/getBidsRecommendations)

    - [SponsoredBrandsBudgetRulesCampaigns](https://advertising.amazon.com/API/docs/en-us/sponsored-brands/3-0/openapi/prod#tag/Budget-rules/operation/GetCampaignsAssociatedWithSBBudgetRule)

    - [SponsoredBrandsBudgetRules](https://advertising.amazon.com/API/docs/en-us/sponsored-brands/3-0/openapi/prod#tag/Budget-rules/operation/GetSBBudgetRulesForAdvertiser)

    - [SponsoredBrandsCampaignsBudgetRules](https://advertising.amazon.com/API/docs/en-us/sponsored-brands/3-0/openapi/prod#tag/Budget-rules/operation/ListAssociatedBudgetRulesForSBCampaigns)

    - [SponsoredBrandsCampaigns](https://advertising.amazon.com/API/docs/en-us/sponsored-brands/3-0/openapi/prod#tag/Campaigns/operation/ListSponsoredBrandsCampaigns)

    - [SponsoredBrandsKeywords](https://advertising.amazon.com/API/docs/en-us/sponsored-brands/3-0/openapi#tag/Keywords/operation/listKeywords)

    - [SponsoredBrandsNegativeKeywords](https://advertising.amazon.com/API/docs/en-us/sponsored-brands/3-0/openapi#tag/Negative-keywords/operation/listNegativeKeywords)

    - [SponsoredBrandsNegativeTargets](https://advertising.amazon.com/API/docs/en-us/sponsored-brands/3-0/openapi#tag/Negative-product-targeting/operation/listNegativeTargets)

    - [SponsoredBrandsProductTargets](https://advertising.amazon.com/API/docs/en-us/sponsored-brands/3-0/openapi#tag/Product-targeting/operation/listTargets)

    - [SponsoredBrandsStoreAssets](https://advertising.amazon.com/API/docs/en-us/sponsored-brands/3-0/openapi#tag/Stores/operation/listAssets)

    - [SponsoredDisplayAdGroups](https://advertising.amazon.com/API/docs/en-us/sponsored-display/3-0/openapi#tag/Ad-Groups/operation/listAdGroupsEx)

    - [SponsoredDisplayBrandSafetyList](https://advertising.amazon.com/API/docs/en-us/sponsored-display/3-0/openapi#tag/Brand-Safety-List/operation/listRequestStatus)

    - [SponsoredDisplayBudgetRulesCampaigns](https://advertising.amazon.com/API/docs/en-us/sponsored-display/3-0/openapi#tag/Budget-Rules/operation/GetCampaignsAssociatedWithSDBudgetRule)

    - [SponsoredDisplayBudgetRules](https://advertising.amazon.com/API/docs/en-us/sponsored-display/3-0/openapi#tag/Budget-Rules/operation/GetSDBudgetRulesForAdvertiser)

    - [SponsoredDisplayCampaignsBudgetRules](https://advertising.amazon.com/API/docs/en-us/sponsored-display/3-0/openapi#tag/Budget-Rules/operation/ListAssociatedBudgetRulesForSDCampaigns)

    - [SponsoredDisplayCampaigns](https://advertising.amazon.com/API/docs/en-us/sponsored-display/3-0/openapi#tag/Campaigns/operation/listCampaignsEx)

    - [SponsoredDisplayCreatives](https://advertising.amazon.com/API/docs/en-us/sponsored-display/3-0/openapi#tag/Creatives/operation/listCreatives)

    - [SponsoredDisplayNegativeTargetingClauses](https://advertising.amazon.com/API/docs/en-us/sponsored-display/3-0/openapi#tag/Negative-Targeting/operation/listNegativeTargetingClausesEx)

    - [SponsoredDisplayProductAds](https://advertising.amazon.com/API/docs/en-us/sponsored-display/3-0/openapi#tag/Product-Ads/operation/listProductAdsEx)

    - [SponsoredDisplayTargetings](https://advertising.amazon.com/API/docs/en-us/sponsored-display/3-0/openapi#tag/Targeting/operation/listTargetingClausesEx)

    - [SponsoredProductsAdGroups](https://advertising.amazon.com/API/docs/en-us/sponsored-products/3-0/openapi/prod#tag/Ad-groups/operation/ListSponsoredProductsAdGroups)

    - [SponsoredProductsAds](https://advertising.amazon.com/API/docs/en-us/sponsored-products/3-0/openapi/prod#tag/Product-ads/operation/ListSponsoredProductsProductAds)

    - [SponsoredProductsBudgetRules](https://advertising.amazon.com/API/docs/en-us/sponsored-products/3-0/openapi/prod#tag/BudgetRules/operation/GetSPBudgetRulesForAdvertiser)

    - [SponsoredProductsCampaigns](https://advertising.amazon.com/API/docs/en-us/sponsored-products/3-0/openapi/prod#tag/Campaigns/operation/ListSponsoredProductsCampaigns)

    - [SponsoredProductsKeywords](https://advertising.amazon.com/API/docs/en-us/sponsored-products/3-0/openapi/prod#tag/Keywords/operation/ListSponsoredProductsKeywords)

    - [SponsoredProductsNegativeKeywords](https://advertising.amazon.com/API/docs/en-us/sponsored-products/3-0/openapi/prod#tag/Negative-keywords/operation/ListSponsoredProductsNegativeKeywords)

- Outputs the schema for each resource
- Incrementally pulls data based on the input state


## Streams


** [invoices](https://advertising.amazon.com/API/docs/en-us/billing#tag/invoice/operation/getAdvertiserInvoices)**
- Data Key = invoiceSummaries
- Primary keys: ['id']
- Replication strategy: INCREMENTAL

** [portfolios](https://advertising.amazon.com/API/docs/en-us/reference/portfolios#tag/Portfolios/operation/ListPortfolios)**
- Data Key = portfolios
- Primary keys: ['portfolioId']
- Replication strategy: INCREMENTAL

** [profiles](https://advertising.amazon.com/API/docs/en-us/reference/2/profiles#tag/Profiles/operation/listProfiles)**
- Primary keys: ['profileId']
- Replication strategy: FULL_TABLE

** [sponsored_brands_ad_creatives](https://advertising.amazon.com/API/docs/en-us/sponsored-brands/3-0/openapi/prod#tag/Ad-creatives/operation/ListCreatives)**
- Data Key = creatives
- Primary keys: ['adId']
- Replication strategy: INCREMENTAL

** [sponsored_brands_ad_groups](https://advertising.amazon.com/API/docs/en-us/sponsored-brands/3-0/openapi/prod#tag/Ad-groups/operation/ListSponsoredBrandsAdGroups)**
- Data Key = adGroups
- Primary keys: ['adGroupId']
- Replication strategy: INCREMENTAL

** [sponsored_brands_ads](https://advertising.amazon.com/API/docs/en-us/sponsored-brands/3-0/openapi/prod#tag/Ads/operation/ListSponsoredBrandsAds)**
- Data Key = ads
- Primary keys: ['adId']
- Replication strategy: INCREMENTAL

** [sponsored_brands_bid_recommendations](https://advertising.amazon.com/API/docs/en-us/sponsored-brands/3-0/openapi#tag/Bid-recommendations/operation/getBidsRecommendations)**
- Primary keys: ['recommendationId']
- Replication strategy: FULL_TABLE

** [sponsored_brands_budget_rules_campaigns](https://advertising.amazon.com/API/docs/en-us/sponsored-brands/3-0/openapi/prod#tag/Budget-rules/operation/GetCampaignsAssociatedWithSBBudgetRule)**
- Data Key = associatedCampaigns
- Primary keys: ['campaignId']
- Replication strategy: FULL_TABLE

** [sponsored_brands_budget_rules](https://advertising.amazon.com/API/docs/en-us/sponsored-brands/3-0/openapi/prod#tag/Budget-rules/operation/GetSBBudgetRulesForAdvertiser)**
- Data Key = budgetRulesForAdvertiserResponse
- Primary keys: ['ruleId']
- Replication strategy: INCREMENTAL

** [sponsored_brands_campaigns_budget_rules](https://advertising.amazon.com/API/docs/en-us/sponsored-brands/3-0/openapi/prod#tag/Budget-rules/operation/ListAssociatedBudgetRulesForSBCampaigns)**
- Data Key = associatedRules
- Primary keys: ['ruleId']
- Replication strategy: INCREMENTAL

** [sponsored_brands_campaigns](https://advertising.amazon.com/API/docs/en-us/sponsored-brands/3-0/openapi/prod#tag/Campaigns/operation/ListSponsoredBrandsCampaigns)**
- Data Key = campaigns
- Primary keys: ['campaignId']
- Replication strategy: INCREMENTAL

** [sponsored_brands_keywords](https://advertising.amazon.com/API/docs/en-us/sponsored-brands/3-0/openapi#tag/Keywords/operation/listKeywords)**
- Primary keys: ['keywordId']
- Replication strategy: FULL_TABLE

** [sponsored_brands_negative_keywords](https://advertising.amazon.com/API/docs/en-us/sponsored-brands/3-0/openapi#tag/Negative-keywords/operation/listNegativeKeywords)**
- Primary keys: ['keywordId']
- Replication strategy: FULL_TABLE

** [sponsored_brands_negative_targets](https://advertising.amazon.com/API/docs/en-us/sponsored-brands/3-0/openapi#tag/Negative-product-targeting/operation/listNegativeTargets)**
- Data Key = negativeTargets
- Primary keys: ['targetId']
- Replication strategy: FULL_TABLE

** [sponsored_brands_product_targets](https://advertising.amazon.com/API/docs/en-us/sponsored-brands/3-0/openapi#tag/Product-targeting/operation/listTargets)**
- Primary keys: ['targetId']
- Replication strategy: FULL_TABLE

** [sponsored_brands_store_assets](https://advertising.amazon.com/API/docs/en-us/sponsored-brands/3-0/openapi#tag/Stores/operation/listAssets)**
- Primary keys: ['assetID']
- Replication strategy: FULL_TABLE

** [sponsored_display_ad_groups](https://advertising.amazon.com/API/docs/en-us/sponsored-display/3-0/openapi#tag/Ad-Groups/operation/listAdGroupsEx)**
- Primary keys: ['adGroupId']
- Replication strategy: INCREMENTAL

** [sponsored_display_brand_safety_list](https://advertising.amazon.com/API/docs/en-us/sponsored-display/3-0/openapi#tag/Brand-Safety-List/operation/listRequestStatus)**
- Data Key = requestStatusList
- Primary keys: ['requestId']
- Replication strategy: FULL_TABLE

** [sponsored_display_budget_rules_campaigns](https://advertising.amazon.com/API/docs/en-us/sponsored-display/3-0/openapi#tag/Budget-Rules/operation/GetCampaignsAssociatedWithSDBudgetRule)**
- Data Key = associatedCampaigns
- Primary keys: ['campaignId']
- Replication strategy: FULL_TABLE

** [sponsored_display_budget_rules](https://advertising.amazon.com/API/docs/en-us/sponsored-display/3-0/openapi#tag/Budget-Rules/operation/GetSDBudgetRulesForAdvertiser)**
- Data Key = budgetRulesForAdvertiserResponse
- Primary keys: ['ruleId']
- Replication strategy: INCREMENTAL

** [sponsored_display_campaigns_budget_rules](https://advertising.amazon.com/API/docs/en-us/sponsored-display/3-0/openapi#tag/Budget-rules/operation/DisassociateAssociatedBudgetRuleForSBCampaigns)**
- Data Key = associatedRules
- Primary keys: ['ruleId']
- Replication strategy: INCREMENTAL

** [sponsored_display_campaigns](https://advertising.amazon.com/API/docs/en-us/sponsored-display/3-0/openapi#tag/Campaigns/operation/listCampaignsEx)**
- Primary keys: ['campaignId']
- Replication strategy: INCREMENTAL

** [sponsored_display_creatives](https://advertising.amazon.com/API/docs/en-us/sponsored-display/3-0/openapi#tag/Creatives/operation/listCreatives)**
- Primary keys: ['creativeId']
- Replication strategy: FULL_TABLE

** [sponsored_display_negative_targeting_clauses](https://advertising.amazon.com/API/docs/en-us/sponsored-display/3-0/openapi#tag/Negative-Targeting/operation/listNegativeTargetingClausesEx)**
- Primary keys: ['targetId']
- Replication strategy: INCREMENTAL

** [sponsored_display_product_ads](https://advertising.amazon.com/API/docs/en-us/sponsored-display/3-0/openapi#tag/Product-Ads/operation/listProductAdsEx)**
- Primary keys: ['adId']
- Replication strategy: INCREMENTAL

** [sponsored_display_targetings](https://advertising.amazon.com/API/docs/en-us/sponsored-display/3-0/openapi#tag/Targeting/operation/listTargetingClausesEx)**
- Primary keys: ['targetId']
- Replication strategy: INCREMENTAL

** [sponsored_products_ad_groups](https://advertising.amazon.com/API/docs/en-us/sponsored-products/3-0/openapi/prod#tag/Ad-groups/operation/ListSponsoredProductsAdGroups)**
- Data Key = adGroups
- Primary keys: ['adGroupId']
- Replication strategy: INCREMENTAL

** [sponsored_products_ads](https://advertising.amazon.com/API/docs/en-us/sponsored-products/3-0/openapi/prod#tag/Product-ads/operation/ListSponsoredProductsProductAds)**
- Data Key = productAds
- Primary keys: ['adId']
- Replication strategy: INCREMENTAL

** [sponsored_products_budget_rules](https://advertising.amazon.com/API/docs/en-us/sponsored-products/3-0/openapi/prod#tag/BudgetRules/operation/GetSPBudgetRulesForAdvertiser)**
- Data Key = budgetRulesForAdvertiserResponse
- Primary keys: ['ruleId']
- Replication strategy: INCREMENTAL

** [sponsored_products_campaigns](https://advertising.amazon.com/API/docs/en-us/sponsored-products/3-0/openapi/prod#tag/Campaigns/operation/ListSponsoredProductsCampaigns)**
- Data Key = campaigns
- Primary keys: ['campaignId']
- Replication strategy: INCREMENTAL

** [sponsored_products_keywords](https://advertising.amazon.com/API/docs/en-us/sponsored-products/3-0/openapi/prod#tag/Keywords/operation/ListSponsoredProductsKeywords)**
- Data Key = keywords
- Primary keys: ['keywordId']
- Replication strategy: INCREMENTAL

** [sponsored_products_negative_keywords](https://advertising.amazon.com/API/docs/en-us/sponsored-products/3-0/openapi/prod#tag/Negative-keywords/operation/ListSponsoredProductsNegativeKeywords)**
- Data Key = negativeKeywords
- Primary keys: ['keywordId']
- Replication strategy: INCREMENTAL

## Authentication

## Quick Start

1. Install

    Clone this repository, and then install using setup.py. We recommend using a virtualenv:

    ```bash
    > virtualenv -p python3 venv
    > source venv/bin/activate
    > python setup.py install
    OR
    > cd .../tap-amazon_ads
    > pip install -e .
    ```
2. Dependent libraries. The following dependent libraries were installed.
    ```bash
    > pip install singer-python
    > pip install target-stitch
    > pip install target-json

    ```
    - [singer-tools](https://github.com/singer-io/singer-tools)
    - [target-stitch](https://github.com/singer-io/target-stitch)

3. Create your tap's `config.json` file.  The tap config file for this tap should include these entries:
   - `start_date` - the default value to use if no bookmark exists for an endpoint (rfc3339 date string)
   - `user_agent` (string, optional): Process and email for API logging purposes. Example: `tap-amazon_ads <api_user_email@your_company.com>`
   - `request_timeout` (integer, `300`): Max time for which request should wait to get a response. Default request_timeout is 300 seconds.

    ```json
    {
        "start_date": "2019-01-01T00:00:00Z",
        "user_agent": "tap-amazon_ads <api_user_email@your_company.com>",
        "request_timeout": 300
    }```

    Optionally, also create a `state.json` file. `currently_syncing` is an optional attribute used for identifying the last object to be synced in case the job is interrupted mid-stream. The next run would begin where the last job left off.

    ```json
    {
        "currently_syncing": "engage",
        "bookmarks": {
            "export": "2019-09-27T22:34:39.000000Z",
            "funnels": "2019-09-28T15:30:26.000000Z",
            "revenue": "2019-09-28T18:23:53Z"
        }
    }
    ```

4. Run the Tap in Discovery Mode
    This creates a catalog.json for selecting objects/fields to integrate:
    ```bash
    tap-amazon_ads --config config.json --discover > catalog.json
    ```
   See the Singer docs on discovery mode
   [here](https://github.com/singer-io/getting-started/blob/master/docs/DISCOVERY_MODE.md).

5. Run the Tap in Sync Mode (with catalog) and [write out to state file](https://github.com/singer-io/getting-started/blob/master/docs/RUNNING_AND_DEVELOPING.md).

    For Sync mode:
    ```bash
    > tap-amazon_ads --config tap_config.json --catalog catalog.json > state.json
    > tail -1 state.json > state.json.tmp && mv state.json.tmp state.json
    ```
    To load to json files to verify outputs:
    ```bash
    > tap-amazon_ads --config tap_config.json --catalog catalog.json | target-json > state.json
    > tail -1 state.json > state.json.tmp && mv state.json.tmp state.json
    ```
    To pseudo-load to [Stitch Import API](https://github.com/singer-io/target-stitch) with dry run:
    ```bash
    > tap-amazon_ads --config tap_config.json --catalog catalog.json | target-stitch --config target_config.json --dry-run > state.json
    > tail -1 state.json > state.json.tmp && mv state.json.tmp state.json
    ```

6. Test the Tap

    While developing the amazon_ads tap, the following utilities were run in accordance with Singer.io best practices:
    Pylint to improve [code quality](https://github.com/singer-io/getting-started/blob/master/docs/BEST_PRACTICES.md).
    ```bash
    > pylint tap_amazon_ads -d missing-docstring -d logging-format-interpolation -d too-many-locals -d too-many-arguments
    ```
    Pylint test resulted in the following score:
    ```bash
    Your code has been rated at 9.67/10
    ```

    To [check the tap](https://github.com/singer-io/singer-tools).
    ```bash
    > tap_amazon_ads --config tap_config.json --catalog catalog.json | singer-check-tap > state.json
    > tail -1 state.json > state.json.tmp && mv state.json.tmp state.json
    ```

    #### Unit Tests

    Unit tests may be run with the following.

    ```
    python -m pytest --verbose
    ```

    Note, you may need to install test dependencies.

    ```
    pip install -e .'[dev]'
    ```
---

Copyright &copy; 2019 Stitch
