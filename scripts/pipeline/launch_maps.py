import json,subprocess,sys
CAT={'deck':["deck builder","general contractor","construction company","contractor","fence contractor","remodeler","carpenter","home builder","custom home builder"],
 'mortgage':["mortgage broker","mortgage lender"],
 'hardscape':["landscaper","paving contractor","landscape designer","masonry contractor","patio enclosure supplier"]}
TERMS={'deck':["deck builder","deck contractor"],'mortgage':["mortgage broker"],'hardscape':["hardscape contractor","paver installer"]}
def launch(tag,niche,locs,charge,per=40):
    inp={'searchStringsArray':[f"{t} in {l}" for l in locs for t in TERMS[niche]],'maxCrawledPlacesPerSearch':per,'language':'en','countryCode':'us',
         'placeMinimumStars':'four','website':'withWebsite','skipClosedPlaces':True,'categoryFilterWords':CAT[niche],
         'scrapeContacts':False,'scrapePlaceDetailPage':False,'maxReviews':0,'maxImages':0}
    u=f"https://api.apify.com/v2/acts/compass~crawler-google-places/runs?maxTotalChargeUsd={charge}"
    r=json.loads(subprocess.run(['curl','-sS','-m','120','-X','POST','-H','Content-Type: application/json','--data-binary','@-',u],input=json.dumps(inp).encode(),capture_output=True).stdout)
    d=r.get('data') or r
    print(tag,niche,len(locs),'locs ->',d.get('id'),d.get('status'),r.get('error'))
    runs=json.load(open('runs.json')) if __import__('os').path.exists('runs.json') else []
    runs.append({'tag':tag,'niche':niche,'locs':locs,'id':d.get('id'),'datasetId':d.get('defaultDatasetId')}); json.dump(runs,open('runs.json','w'),indent=1)
if __name__=='__main__':
    launch(sys.argv[1],sys.argv[2],json.loads(sys.argv[3]),sys.argv[4])
