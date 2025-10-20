# find .smreward paths
# loop through articles
# check the ones that are younger than a week (config?)
# loop comments
# select the ones that aren't checked
# show the url
# get user input whether to accept it or not
# if accept, create reward
import glx.helper as helper
import os
import datetime
from glx.community import Community
import datetime
import subprocess
import csv
import sys

APPNAME = "smreward"

def main():
    config = helper.load_app_config(APPNAME)
    
    # loop through articles
    community = Community(config["community_name"])
    collection = community.collection(config["collection_id"])
    articles = community.articles()
    for article in articles:
        if config["tag"] in article.data("meta_keywords") and not article.is_expired(int(config["expiry_days"])):
            # check the ones that are younger than a week
            loadpath = os.path.join("."+APPNAME,str(article.id))
            fn = os.path.join(loadpath,"article.json")
            if os.path.exists(fn):
                a = helper.load_json(fn)
                print(a)
            
            # loop files in the folder
            comments = article.comments()
            loadpath = os.path.join("."+APPNAME,str(article.id),"x")
            for f in os.listdir(loadpath):
                print(f)
                # load file and check if it was processed yet
                comment_file = os.path.join(loadpath,f)
                comment = helper.load_json(comment_file)
                if not comment["checked"]:
                    if "auto" in sys.argv:
                        # build the automatic checker here
                        # find username
                        parts = comment["link"].split("?")[0]
                        parts = parts.split("/")
                        print(parts)
                        username =  parts[3]
                        print("username:",username)
                        # find the id
                        xid = parts[5]
                        # get last 5 tweet
                        a = subprocess.run("python scraper -u gergelyfabian1 -t 5", shell=True, capture_output=True, text=True)
                        print(a)
                        # find csv filename
                        # loop through and find the one with the right id
                        # check for parts
                        # suggest decision
                        # spell out problems

                    #print link
                    print("owner:",comment["owner_id"])
                    print("required:",comment["required"])
                    print("link:",comment["link"])
                    appr = input("Approve? (y/n)")

                    if appr.lower() == "y":
                        # grant reward
                        card = collection.card(comment["owner_id"])
                        card.increase_attribute_value(config["reward_id"],config["reward_amount"])    
                        comment["action"]= "Reward "+str(config["reward_amount"])+" to "+str(config["reward_id"])+" added."
                        print(card.id,"increased reward")
                    else:
                        comment["action"]= "Reward denied."

                    # set checked to true
                    comment["checked"]=True
                    comment["action_at"] = datetime.datetime.now().isoformat()

                    helper.save_as_json(comment_file,comment)
