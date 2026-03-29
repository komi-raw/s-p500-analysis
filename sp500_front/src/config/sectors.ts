export type Sector = {
    name: string;
    color: string;
    tickers: string[];
};

export const SECTORS: Sector[] = [
    {
        name: "Information Technology",
        color: "#3b82f6",
        tickers: ["AAPL","MSFT","NVDA","AVGO","ORCL","CRM","ACN","CSCO","AMD","TXN","INTU","IBM","AMAT","NOW","KLAC","ADI","LRCX","SNPS","CDNS","ANET","PANW","FTNT","MCHP","HPQ","HPE","CTSH","IT","GDDY","CDW","NTAP","PTC","JKHY","TER","FFIV","SMCI","PLTR","DDOG","DELL"],
    },
    {
        name: "Health Care",
        color: "#10b981",
        tickers: ["UNH","JNJ","LLY","ABBV","MRK","ABT","TMO","AMGN","DHR","ISRG","MDT","ELV","CVS","CI","SYK","BSX","ZTS","VRTX","REGN","MCK","BDX","IDXX","BIIB","HOLX","BAX","IQV","CNC","HCA","HUM","DXCM","MOH","MTD","PODD","RMD","GEHC","CRL","RVTY","TECH","DGX","LH","MRNA"],
    },
    {
        name: "Financials",
        color: "#f59e0b",
        tickers: ["JPM","BAC","WFC","GS","MS","C","BLK","SCHW","AXP","PNC","USB","TFC","COF","MET","PRU","AIG","CB","MMC","ICE","CME","CBOE","MSCI","MCO","SPGI","AON","MA","V","PYPL","FI","FIS","FITB","HBAN","RF","CFG","MTB","NTRS","IVZ","BK","STT","CINF","ERIE","GL","AIZ","BEN","AMP","BX","KKR","RJF","IBKR","HOOD","COIN"],
    },
    {
        name: "Consumer Discretionary",
        color: "#ec4899",
        tickers: ["AMZN","TSLA","HD","MCD","NKE","LOW","TJX","BKNG","CMG","MAR","YUM","HLT","ROST","ORLY","AZO","DHI","LEN","PHM","NVR","RCL","CCL","NCLH","MGM","LVS","WYNN","EBAY","ULTA","BBY","TPR","RL","DECK","LKQ","KMX","MHK","POOL","DRI","BLDR"],
    },
    {
        name: "Communication Services",
        color: "#8b5cf6",
        tickers: ["META","GOOGL","GOOG","NFLX","CMCSA","DIS","T","VZ","TMUS","FOXA","FOX","OMC","IPG","TTWO","EA","DASH","MTCH","LYV","TKO","NWSA","NWS","WBD","CHTR"],
    },
    {
        name: "Industrials",
        color: "#64748b",
        tickers: ["RTX","HON","UPS","BA","CAT","DE","LMT","GE","GEV","ETN","EMR","ITW","FDX","WM","RSG","CSX","UNP","NSC","NOC","GD","HII","LHX","TDG","TXT","PWR","OTIS","CARR","PCAR","CTAS","EXPD","JBHT","CHRW","DAL","UAL","LUV","LDOS","AME","DOV","IR","ROP","IEX","NDSN","HWM","GWW","HUBB","EME","SNA","ODFL","FTV","GNRC","DAY"],
    },
    {
        name: "Consumer Staples",
        color: "#84cc16",
        tickers: ["WMT","PG","KO","PEP","MDLZ","COST","PM","MO","CL","KHC","GIS","STZ","SYY","K","CPB","HRL","SJM","MKC","CHD","CLX","HSY","MNST","KDP","TAP","KR","KVUE","BG","LW","EL"],
    },
    {
        name: "Energy",
        color: "#f97316",
        tickers: ["XOM","CVX","COP","SLB","EOG","PSX","MPC","OXY","FANG","DVN","APA","EQT","HAL","BKR","CTRA","TRGP","OKE","WMB","KMI","EXE"],
    },
    {
        name: "Real Estate",
        color: "#06b6d4",
        tickers: ["PLD","AMT","EQIX","CCI","SPG","O","WELL","DLR","PSA","EQR","AVB","ARE","VTR","BXP","MAA","CPT","REG","DOC","UDR","IRM","SBAC","EXR","ESS","HST","FRT","INVH"],
    },
    {
        name: "Materials",
        color: "#a78bfa",
        tickers: ["LIN","APD","SHW","FCX","NEM","ECL","NUE","STLD","ALB","DD","PPG","EMN","LYB","IP","PKG","AMCR","AVY","CE","MLM","VMC","MOS","CF","BALL","IFF","DOW"],
    },
    {
        name: "Utilities",
        color: "#2dd4bf",
        tickers: ["NEE","DUK","SO","D","AEP","EXC","XEL","ED","ES","AWK","EIX","PPL","FE","ETR","DTE","CMS","AES","LNT","CNP","EVRG","NI","NRG","AEE","PNW","PCG","SRE"],
    },
];
