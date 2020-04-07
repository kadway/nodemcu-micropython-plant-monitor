def web_page(spi_out, spi_in):

    html = """<html><head> <title>Main Page - Johny's ESP Web Server</title> <meta http-equiv="refresh" content="1" >
  <link rel="icon" href="data:,">
  <style>html{font-family: Helvetica; display:inline-block; margin: 0px auto; text-align: center;}
  h1{color: #0F3376; padding: 2vh;}p{font-size: 1.5rem;}.button{display: inline-block; background-color: #e7bd3b; border: none; 
  border-radius: 4px; color: white; padding: 16px 40px; text-decoration: none; font-size: 30px; margin: 2px; cursor: pointer;}
  .button2{background-color: #4286f4;}</style></head>

  <body> 
  <h1>Johny's ESP Web Server this is a test!</h1> 

  <p>spi_out: <strong>""" + spi_out + """</strong></p>
  <p>spi_in: <strong>""" + spi_in + """</strong></p>

  <p><a href="/?refresh=now"><button class="button">refresh</button></a></p>

  </body></html>"""

    return html

# <meta name="viewport" content="width=device-width, initial-scale=1">