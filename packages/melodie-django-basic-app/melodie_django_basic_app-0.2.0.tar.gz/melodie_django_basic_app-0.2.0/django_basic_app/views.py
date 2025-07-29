from django.http import HttpResponse

def description(request):
    html = """
    <html>
      <head>
        <title>Mélodie's App</title>
        <style>
          body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #ffffff;
            color: #003366; /* Navy blue */
            margin: 50px;
            text-align: center;
          }
          h1 {
            font-weight: 700;
            font-size: 2.5rem;
            margin-bottom: 20px;
          }
          p {
            font-size: 1.2rem;
            max-width: 600px;
            margin: 0 auto 15px auto;
            line-height: 1.6;
          }
        </style>
      </head>
      <body>
        <h1>Welcome to Mélodie's Django App</h1>
        <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed non risus. Suspendisse lectus tortor, dignissim sit amet, adipiscing nec, ultricies sed, dolor.</p>
        <p>Cras elementum ultrices diam. Maecenas ligula massa, varius a, semper congue, euismod non, mi.</p>
      </body>
    </html>
    """
    return HttpResponse(html)
