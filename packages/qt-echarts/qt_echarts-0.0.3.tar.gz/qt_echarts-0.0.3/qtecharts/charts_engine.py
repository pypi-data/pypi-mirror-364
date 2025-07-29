import json

from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtWebEngineWidgets import QWebEngineView
from pyecharts.charts.chart import Chart

from qtecharts.utils.chart_chanel import ChartChanel


class ChartEngine(QWebEngineView):

    def __init__(self, parent=None, chart: Chart = None, on_click=None):
        super().__init__(parent)
        self.chart = chart
        self.html_content = ""
        self.on_click = on_click
        self.chanel = QWebChannel()
        self.page().setWebChannel(self.chanel)
        self.init_engine()
        self.channel = ChartChanel(func=self.from_web)
        self.chanel.registerObject("con", self.channel)

    def init_engine(self):
        self.init_chart()
        self.setHtml(self.html_content)
        self.page().loadFinished.connect(self.init_on_click)

    def from_web(self, msg):
        data = json.loads(msg)
        if self.on_click is not None:
            self.on_click(data)

    def init_chart(self):
        if self.chart is not None:
            self.chart.width = "100%"
            self.chart.height = "calc(100vh - 20px)"
            self.html_content = self.chart.render_embed()
            self.init_channel()

    def init_channel(self):
        from bs4 import BeautifulSoup
        from lxml import html
        html_str = BeautifulSoup(self.html_content, "html.parser").prettify()
        html_xp = html.fromstring(html_str)
        head_tag = html_xp.xpath('//head')[0]

        # 添加 Qt WebChannel（你已经有的）
        script_qt = html.Element("script")
        script_qt.attrib["src"] = "qrc:///qtwebchannel/qwebchannel.js"
        script_qt.attrib["type"] = "text/javascript"
        head_tag.insert(1, script_qt)

        custom_js = """
                    <script language="JavaScript">
                        function Web2PyQt5Value(data) {
                            if (window.con) {
                             function removeCircularReferences(obj, seen = new WeakSet()) {
                                if (typeof obj !== 'object' || obj === null) {
                                    return obj;
                                }
                                if (seen.has(obj)) {
                                    return '[Circular]';
                                }
                                seen.add(obj);
                                if (Array.isArray(obj)) {
                                    return obj.map(item => removeCircularReferences(item, seen));
                                } else {
                                    const result = {};
                                    for (const key in obj) {
                                        if (obj.hasOwnProperty(key)) {
                                            result[key] = removeCircularReferences(obj[key], seen);
                                        }
                                    }
                                    return result;
                                }
                            }
                                const safeData = removeCircularReferences(data);
                                con.js_to_qt(JSON.stringify(safeData))
                            }
                        }
                        function PyQt52WebValue(value){
                            alert(value);
                        }

                        new QWebChannel(qt.webChannelTransport, function(channel) {
                            window.con = channel.objects.con;
                        });

                    </script>
                    """
        head_tag.insert(2, html.fromstring(custom_js))
        self.html_content = html.tostring(html_xp, encoding='unicode', pretty_print=True)

    def save_html_file(self, path):
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.html_content)

    def init_on_click(self):
        js = """
        var chartDom = document.getElementById('%s'); // 获取图表实例
        window.chart = echarts.getInstanceByDom(chartDom);
        if (chart){
            chart.on('click', function (params) {
                console.log(params);
               Web2PyQt5Value(params)
            
            });
        }
        """ % self.chart.chart_id
        self.page().runJavaScript(js)
