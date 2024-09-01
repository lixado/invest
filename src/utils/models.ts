interface FundResult {
    instrument_info: InstrumentInfo;
    price_info: PriceInfo;
    historical_returns_info: HistoricalReturnsInfo;
    fund_info: FundInfo;
    annual_growth_info: AnnualGrowthInfo;
    statistical_info: StatisticalInfo;
}

interface InstrumentInfo {
    name: string;
    instrument_icon_url: string;
}

interface PriceInfo {
    last: {
        price: number;
        decimals: number;
    };
    tick_timestamp: number;
    realtime: boolean;
}

interface HistoricalReturnsInfo {
    yield_1d: number;
    yield_1w: number;
    yield_1m: number;
    yield_3m: number;
    yield_ytd: number;
    yield_1y: number;
    yield_3y: number;
    yield_5y: number;
    realtime: boolean;
}

interface FundInfo {
    fund_type: string;
    fund_category: string;
    fund_universe_country: string;
    fund_universe_currency: string;
    fund_universe_ids: number[];
    fund_admin_company: string;
    fund_nordnet_selection: boolean;
    fund_total_market_value: number;
    fund_esg_score: number;
    fund_yearly_fee: number;
    fund_calculated_fee: number;
    fund_platform_fee: number;
    fund_refunding: number;
    fund_raw_risk: number;
    fund_risk_group: string;
    fund_start_date: number;
    fund_trading_frequency: string;
    fund_branding_company: string;
    fund_min_investment: number;
    fund_dividend_strategy: string;
    fund_raw_sfdr: number;
    fund_sfdr_article: string;
}

interface AnnualGrowthInfo {
    annual_growth_1y: number;
    annual_growth_3y: number;
    annual_growth_5y: number;
}

interface StatisticalInfo {
    statistics_timestamp: number;
    number_of_owners: number;
}

interface Bank {
    date: string;
    product_id: string;
    version_id: string;
    navn: string;
    published: string;
    publiserFra: string;
    publiserTil: string;
    leverandorId: string;
    leverandorUrl: string;
    leverandorHref: string;
    leverandorVisningsnavn: string;
    markedsomraade: string;
    markedsomraadeTekst: string;
    totaltInnestaende: string;
    effectivRente: string;
    nominellRente: string;
    rentebelop: string;
    totalbelop: string;
    minAlder: string;
    maksAlder: string;
    trenger_ikke_pakke: string;
    produktpakkeNavn: string;
    produktpakkeHref: string;
    forutsettermedlemskap: string;
    medlemskapNavn: string;
    medlemskapHref: string;
    kap_periode: string;
    trapp_type: string;
    rentesats1: string;
    rentesats2: string;
    rentesats3: string;
    rentesats4: string;
    rentesats5: string;
    rentesats6: string;
    grensebelop1: string;
    grensebelop2: string;
    grensebelop3: string;
    grensebelop4: string;
    grensebelop5: string;
    grensebelop6: string;
    frie_uttak: string;
}

interface AutocompleteOption {
    index: number;
    name: string;
    icon_url: string;
    interest_rate: number;
}

export type { AutocompleteOption, Bank, FundResult, InstrumentInfo, PriceInfo, HistoricalReturnsInfo, FundInfo, AnnualGrowthInfo, StatisticalInfo };
