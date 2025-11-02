import sys
import glx.helper as helper
from glx.community import Community
import os
import datetime
import glx.apphelper
import argparse
import pprint

APPNAME = "smreward"
__version__ = "0.5.1"
CONFIG_TEMPLATE = "config_template.toml"

def main(community_name):
    config = helper.load_app_config(community_name,APPNAME,config_template)
    
    collection = Community(community_name).collection(1)
    for article in active_articles(community_name,config["expiry_days"],config["tag"]):
        # preprocessing comments
        # to deal with multiple entries by the same user
        comments = {}
        for comment in article.comments():
            status = comment_status(community_name,comment,article.id)
            card_id = comment["author_card_id"]
            if not card_id in comments.keys() or comments[card_id]["status"] == "denied":
                comments[card_id]={"status":status,"comment":comment}

        for card_id,v in comments.items():
            comment = v["comment"]
           
            if v["status"] == "UNPROCESSED":
                # there was no decision yet.
                # if it does not have an x link then it's auto denied
                if not ("https://x.com" in comment["content"] or "https://twitter.com" in comment["content"]):
                    decision = "denied"
                    reason = "No X link"
                else:
                    if config["auto_approve"]:
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
                    "required": ["@galaxisxyz",community_name]
                }

                if decision == "approved":
                    card = collection.card(struct["owner_id"])
                    card.increase_attribute_value(config["reward_id"],config["reward_amount"],7*60*24)    
                    action = "Reward "+str(config["reward_amount"])+" to "+str(config["reward_id"])+" added."
                    struct["action"]= action

                filename = construct_filename(article.id,comment["author_card_id"],comment["id"])
                helper.save_app_data(community_name,APPNAME,filename,struct)

def construct_filename(article_id, author_card_id, comment_id):
    return str(article_id)+"_x_"+str(author_card_id)+"_"+str(comment_id)+".json"

def comment_status(community_name,comment,article_id):
    filename = construct_filename(article_id,comment["author_card_id"],comment["id"])
    dec = helper.load_app_data(community_name,APPNAME,filename)
    if not dec:
        return "UNPROCESSED"
    else:
        return dec["decision"] 

def all_articles(community_name,tag):
    # lists all articles with the relevant tag
    # (that is defined in the smreward config)
    articles = []
    for article in Community(community_name).articles():
        if tag in article.data("meta_keywords"):
            articles.append(article)
    return articles

def active_articles(community_name,expiry_days,tag):
    articles = []
    for article in all_articles(community_name,tag):
        if not article.is_expired(int(expiry_days)):
            articles.append(article)
    return articles

def cli():
    parser = glx.apphelper.setup_parser()
    parser.add_argument("-v", "--version", action="store_true")
    parser.add_argument("-p", "--process", action="store_true")
    parser.add_argument("-l", "--list")
    parser.add_argument("--comments")
    args = parser.parse_args()
    
    community_name = glx.apphelper.process_common_args(args,__version__,APPNAME)

    if args.list:
        if args.list == "active":
            for a in active_articles():
                print(a.dt["id"], a.dt["created_at"],a.dt["title"])
        elif args.list == "all":
            for a in all_articles():
                print(a.dt["id"], a.dt["created_at"],a.dt["title"])
    elif args.comments:
        # get the comments of a specific article
        # get the article
        comments = Community(community_name).articles(id=args.comments).comments()
        for comment in comments:
            print(comment['id'],comment['author_card_id'],comment_status(community_name,comment,args.comments))
    elif args.process:
        main(args.community)
