const char MAIN_page[] PROGMEM = R"=====(
<!DOCTYPE html>
<html>
<head>
    <title>Valor do Sensor em Tempo Real</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
</head>
<body>
    <h1>Valor do Sensor em Tempo Real</h1>
    <div id="chart" style="width: 80%; height: 300px;"></div>
    <script>
        var data = [
            { x: [], y: [], type: 'line', name: 'Média Amostral' },
            { x: [], y: [], type: 'scatter', mode: 'markers', name: 'Picos' }
        ];
        var layout = { title: 'Gráfico em Tempo Real' };
        Plotly.newPlot('chart', data, layout);
        var updateInterval = 1000;  // Atualize a cada 1 segundo

        function updateChart() {
            var xhttp = new XMLHttpRequest();
            xhttp.open('GET', '/sensor', true);
            xhttp.onreadystatechange = function() {
                if (xhttp.readyState == 4 && xhttp.status == 200) {
                    var response = JSON.parse(xhttp.responseText);
                    var timestamp = new Date();

                    // Adicione o valor da média amostral ao primeiro conjunto de dados
                    Plotly.extendTraces('chart', { x: [[timestamp]], y: [[response.mediaAmostral]] }, [0]);

                    // Adicione o valor do pico ao segundo conjunto de dados
                    Plotly.extendTraces('chart', { x: [[timestamp]], y: [[response.pico]] }, [1]);
                }
            };
            xhttp.send();
            setTimeout(updateChart, updateInterval);
        }
        updateChart();
    </script>
</body>
</html>

)=====";
