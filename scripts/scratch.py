url = 'https://wcc.sc.egov.usda.gov/nwcc/tabget?state=AK'
br = mechanize.Browser()
br.set_handle_robots(False)
br.open(url)
br.select_form(method='get')
item = br.find_control(name="stationidname").get("49M08SIndian")
item.selected = True
blah = br.submit()
content = blah.read()
