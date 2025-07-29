# QT-Echarts

## 安装
```bash
pip install qt-echarts
```

## 例子

```python

import sys
from pyecharts.charts import Tree
from PyQt5.QtWidgets import QApplication
from pyecharts import options as opts

from qtecharts.charts_engine import ChartEngine

if __name__ == '__main__':
    data = [
        {
            "children": [
                {"name": "B"},
                {
                    "children": [{"children": [{"name": "I"}], "name": "E"}, {"name": "F"}],
                    "name": "C",
                },
                {
                    "children": [
                        {"children": [{"name": "J"}, {"name": "K"}], "name": "G"},
                        {"name": "H"},
                    ],
                    "name": "D",
                },
            ],
            "name": "A",
        }
    ]
    tree = Tree()
    tree.add("",data)
    tree.set_global_opts(title_opts=opts.TitleOpts(title="Tree-基本示例"))
    app = QApplication(sys.argv)

    engine = ChartEngine(chart=tree)

    engine.show()

    sys.exit(app.exec_())


```