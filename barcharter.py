#!/usr/bin/python

import sys
skip_ips = ["93.97.158.26"]
html_template_head = """
<html>
  <head>
    <script type="text/javascript" src="http://www.google.com/jsapi"></script>
    <script type="text/javascript">
      google.load("visualization", "1", {packages:["imagebarchart"]});
      google.setOnLoadCallback(drawChart);
      function drawChart() {
        var data = new google.visualization.DataTable();
        """

html_template_foot = """
        var chart = new google.visualization.ImageBarChart(document.getElementById('chart_div'));
        chart.draw(data, {width: 400, height: 240, min: 0});
      }
    </script>
  </head>
  <body>
    <div id='chart_div' style='width: 700px; height: 240px;'></div>
  </body>
</html>
"""
cols_html = """
        data.addColumn('string', 'Source');
        data.addColumn('number', 'Count');"""
row_html = """
        data.setValue(%d, 0, '%s');
        data.setValue(%d, 1, %d);
"""        
data_html = "%(count)s, undefined, undefined"

def get_data(file_handle):
    name = file_handle.name.split("/")[-1].split(".")[0]
    count = 0
    for row in file_handle.readlines():
        ip = row.split()[0]
        if ip in skip_ips:
            continue
        count += 1
        skip_ips.append(ip)
    return name, count
    
def plot_data(sources):
    html = html_template_head
    html += cols_html
    html += "       data.addRows(%d);" % len(sources)
    idx = 0
    for name, count in sources:
        html += row_html % (idx, name, idx, count);
        idx += 1
    html += html_template_foot
    print html

sources = [get_data(open(x, "r")) for x in sys.argv[1:]]
plot_data(sources)
