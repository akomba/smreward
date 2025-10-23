import sys
import glx.helper as helper
from glx.community import Community
import os
import datetime
import glx.apphelper
import argparse
import pprint

APPNAME = "smreward"
__version__ = "0.5"
CONFIG_TEMPLATE = {
    "tag":False,
    "expiry_days":7,
    "reward_id":False,
    "reward_amount":1,
    "collection_id":1,
    "auto_approve":True
}

CONFIG = {}
COMMUNITY_NAME = None

def main(community_name):
    global CONFIG
    global COMMUNITY_NAME
    init(community_name)
    
    collection = Community(COMMUNITY_NAME).collection(1)
    for article in active_articles():
        # preprocessing comments
        # to deal with multiple entries by the same user
        comments = {}
        for c in article.comments():
            status = comment_status(c,article.id)
            card_id = c["author_card_id"]
            if not card_id in comments.keys() or comments[card_id]["status"] == "denied":
                comments[card_id]={"status":status,"comment":c}

        for card_id,v in comments.items():
            status = v["status"]
            comment = v["comment"]
           
            if status == "UNPROCESSED":
                # there was no decision yet.
                # if it does not have an x link then it's auto denied
                if not ("https://x.com" in comment["content"] or "https://twitter.com" in comment["content"]):
                    decision = "denied"
                    reason = "No X link"
                else:
                    if CONFIG["auto_approve"]:
                        decision = "approved"
                        reason = ""
                    else:
                        # this needs manual processing
                        decision = "deferred"
                        reason = ""
                        
                struct = {
                    "content":comment["content"],
                    "decision": decision,
                    "reason": reason,
                    "owner_id": comment["author_card_id"],
                    "required": ["@galaxisxyz",COMMUNITY_NAME]
                }

                if decision == "approved":
                    card = collection.card(struct["owner_id"])
                    card.increase_attribute_value(CONFIG["reward_id"],CONFIG["reward_amount"],7*60*24)    
                    action = "Reward "+str(CONFIG["reward_amount"])+" to "+str(CONFIG["reward_id"])+" added."
                    struct["action"]= action

                filename = construct_filename(article.id,comment["author_card_id"],comment["id"])
                helper.save_app_data(community_name,APPNAME,filename,struct)

def construct_filename(article_id, author_card_id, comment_id):
    return str(article_id)+"_x_"+str(author_card_id)+"_"+str(comment_id)+".json"

def comment_status(comment,article_id):
    filename = construct_filename(article_id,comment["author_card_id"],comment["id"])
    dec = helper.load_app_data(COMMUNITY_NAME,APPNAME,filename)
    if not dec:
        return "UNPROCESSED"
    else:
        return dec["decision"] 

def init(community_name):
    global CONFIG
    global COMMUNITY_NAME
    COMMUNITY_NAME = community_name
    CONFIG = helper.load_app_config(community_name,APPNAME)

def all_articles():
    global CONFIG
    global COMMUNITY_NAME
    # lists all articles with the relevant tag
    # (that is defined in the smreward config)
    articles = []
    print("community:>",COMMUNITY_NAME)
    for article in Community(COMMUNITY_NAME).articles():
        if CONFIG["tag"] in article.data("meta_keywords"):
            articles.append(article)
    return articles

def active_articles():
    global CONFIG
    global COMMUNITY_NAME
    articles = []
    for article in all_articles():
        if not article.is_expired(int(CONFIG["expiry_days"])):
            articles.append(article)
    return articles

def show_config():
    global CONFIG
    global COMMUNITY_NAME
    print(helper.config_location(COMMUNITY_NAME,APPNAME))
    pprint.pprint(CONFIG,indent=4)

def run():
    global CONFIG
    global COMMUNITY_NAME
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--version", action="store_true")
    parser.add_argument("-r", "--run", action="store_true")
    parser.add_argument("-c", "--community")
    parser.add_argument("-l", "--list")
    parser.add_argument("--config", action="store_true")
    parser.add_argument("--comments")
    args = parser.parse_args()

    if args.version:
        print(__version__)
        exit(0)
   
    if not args.community:
        print(APPNAME,"No community name is given, exiting. (1)")
        exit(0)
    
    init(args.community)
    
    if args.config:
        show_config()
        exit(0)

    if args.community and args.list:
        if args.list == "active":
            for a in active_articles():
                print(a.dt["id"], a.dt["created_at"],a.dt["title"])
        elif args.list == "all":
            for a in all_articles():
                print(a.dt["id"], a.dt["created_at"],a.dt["title"])
    elif args.community and args.comments:
        # get the comments of a specific article
        # get the article
        comments = Community(COMMUNITY_NAME).articles(id=args.comments).comments()
        for comment in comments:
            print(comment['id'],comment['author_card_id'],comment_status(comment,args.comments))
    elif args.community and args.run:
        main(args.community)
    #else:
    #    main(args.community)
    # show status (and rewards) of a specific article
    # show status (and rewards) of a specific card
