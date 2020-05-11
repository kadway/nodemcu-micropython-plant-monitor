def web_page(spi_out, spi_in, i):

    html = """<html><head> <title>Main Page - Johny's ESP Web Server</title> <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="icon" href="data:,">
  <style>html{font-family: Helvetica; display:inline-block; margin: 0px auto; text-align: center;}
  h1{color: #0F3376; padding: 2vh;}p{font-size: 1.5rem;}.button{display: inline-block; background-color: #e7bd3b; border: none; 
  border-radius: 4px; color: white; padding: 16px 40px; text-decoration: none; font-size: 30px; margin: 2px; cursor: pointer;}
  .button2{background-color: #4286f4;}</style></head>

  <body> 
  <h1>Johny's ESP Web Server SPI test nr: <strong>""" + i + """</strong></h1> 


  <p><a href="/?spitest1=now"><button class="button">Configuration</button></a></p>
  <p><a href="/?spitest2=now"><button class="button">Area</button></a></p>
  <p><a href="/?spitest3=now"><button class="button">ADC</button></a></p>
  <p><a href="/?spitest4=now"><button class="button">Actuation</button></a></p>
  <button onclick="myFunction()">Click me</button>
  <p id="demo"></p>
  <script>
    function myFunction() {
        document.getElementById("demo").innerHTML = "Hello World";
    }
  </script>
  </body></html>"""

    return html

# <meta http-equiv="refresh" content="1" >
 # <p>spi_out: <strong>""" + spi_out + """</strong></p>
 # <p>spi_in: <strong>""" + spi_in + """</strong></p>