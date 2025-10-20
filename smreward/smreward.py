import sys
import glx.helper as helper
from glx.community import Community
import os
import datetime
import argparse
import glx.apphelper

APPNAME = "smreward"
__version__ = "0.0.2"
CONFIG_TEMPLATE = {
    "tag":False,
    "expiry_days":7,
    "reward_id":False,
    "reward_amount":1,
    "collection_id":1,
    "auto_approve":True
}

def main(community_name=None):
    # a galaxis app that checks comments under articles
    # finds twitter links
    # reads tweets
    # checks tags
    # rewards smreward with badge
    parser,community_name = glx.apphelper.appstart(__version__,community_name)
    config = helper.load_or_create_app_config(community_name,APPNAME,CONFIG_TEMPLATE)

    # read news post with smreward tags
    # make sure they are not older than 1 week
    # loop through posts
    #   read comments of post
    #   if there is a twitter link, read it through nitter
    #   check for tag
    #   compare that with commenter's card id
    #   save tweet content
    #   add bonus and set expiry for post-date+1week
    
    articles = Community(community_name).articles()
    collection = Community(community_name).collection(1)
    for article in articles:
        if config["tag"] in article.data("meta_keywords") and not article.is_expired(int(config["expiry_days"])):
            print(article.data("title"),article.data("created_at"),article.data("meta_keywords"))
            # save article creation time
            # use it for accepting new comments deadline.
            # do we need this at all? I don't think so.
            # we simply won't check comments on articles that are too old.
            #filename = "article"+"_"+str(article_id)
            #struct = {"created_at":article.data("created_at")}
            #if not helper.load_app_data(community_name,APPNAME,filename):
            #    helper.save_app_data(community_name,APPNAME,filename,struct)


            # get comments
            comments = article.comments()
            for comment in comments:
                #print(comment["author_card_id"],comment["content"])
                # if there is an x link, save details into a folder for manual checks
                #print(comment)
                if "https://x.com" in comment["content"]:
                    filename = os.path.join(str(article.id)+"_x_"+str(comment["author_card_id"])+".json")
                    xlink = comment["content"].split("https://x.com")[1]
                    xlink = "https://x.com"+xlink.split(" \n")[0]
                    struct = {
                        "content":comment["content"],
                        "link": xlink,
                        "checked": False,
                        "owner_id": comment["author_card_id"],
                        "required": ["@galaxisxyz",community_name]
                    }
                    if not helper.load_app_data(community_name,APPNAME,filename):
                        if config["auto_approve"]:
                            print("auto approve!!!")
                            # we auto approve every comment with an x link
                            struct["action"]= "Reward "+str(config["reward_amount"])+" to "+str(config["reward_id"])+" added."

                            # let's distribute the reward
                            card = collection.card(struct["owner_id"])
                            card.increase_attribute_value(config["reward_id"],config["reward_amount"])    

                        helper.save_app_data(community_name,APPNAME,filename,struct)


if __name__ == "__main__":
    main()
