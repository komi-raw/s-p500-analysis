import { createChart } from "lightweight-charts";

export class ChartDefault {
    id!: string;
    chartType!: any;
    chart!: any;
    chartData!: any;

    constructor(
        destId: string,
        chartType: any,
        optionsChart: any = null,
        optionsData: any = null,
    ) {
        this.id = destId;
        this.chartType = chartType;
        this.initChart(optionsChart);
        this.initChartData(optionsData);
    }

    private initChart(options = null) {
        this.chart = createChart(
            document.getElementById(this.id) as HTMLElement,
            options
                ? options
                : {
                      autoSize: true,
                      layout: {
                          background: { color: "#222" },
                          textColor: "#DDD",
                      },
                      grid: {
                          vertLines: { color: "#444" },
                          horzLines: { color: "#444" },
                      },
                  },
        );
    }

    private initChartData(options = null) {
        this.chartData = this.chart.addSeries(this.chartType);

        this.chartData.applyOptions(
            options
                ? options
                : {
                      wickUpColor: "rgb(54, 116, 217)",
                      upColor: "rgb(54, 116, 217)",
                      wickDownColor: "rgb(225, 50, 85)",
                      downColor: "rgb(225, 50, 85)",
                      borderVisible: false,
                  },
        );
    }

    public registerData(data: any) {
        this.chartData.setData(data);
    }

    public fitContent() {
        this.chart.timeScale().fitContent();
    }
}
