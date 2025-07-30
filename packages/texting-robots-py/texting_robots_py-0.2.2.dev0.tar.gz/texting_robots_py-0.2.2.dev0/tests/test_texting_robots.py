from texting_robots import Robot


def test_smoke():
    txt = b'''
    User-Agent: FerrisCrawler
    Allow: /ocean
    Disallow: /rust
    Disallow: /forest*.py
    Crawl-Delay: 10
    User-Agent: *
    Disallow: /
    Sitemap: https://www.example.com/site.xml
    '''

    robot = Robot('FerrisCrawler', txt)

    assert robot.delay == 10

    assert robot.sitemaps == ['https://www.example.com/site.xml']

    assert robot.allowed('https://www.rust-lang.org/ocean')
    assert robot.allowed('/ocean')
    assert robot.allowed('/ocean/reef.html')
    assert not robot.allowed('/rust')
    assert not robot.allowed('/forest/tree/snake.py')
