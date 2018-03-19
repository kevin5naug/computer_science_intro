

class Twitter:
    def __init__(self):
        self.all_users = []
        self.all_tweets = {}

    def get_users(self):
        return self.all_users

    def get_num_users(self):
        return len(self.all_users)

    def get_tweets(self, following):
        # TODO: Implement this function
        # After you implement the method, remember to delete pass
        tweetlst=[]
        for target in following:
            tweetlst.append((target,self.all_tweets[target]))
        result=[]
        for item in tweetlst:
            if len(item[1])>=10:
                for index in range(10):
                    result.append((item[0],item[1][index]))
            elif len(item[1])>=1:
                for tweet in item[1]:
                    result.append((item[0],tweet))
        return result
        
    def add_user(self,new):
        self.all_users.append(new)

    def add_tweet(self, user, tweet):
        # TODO: Implement this function
        # After you implement the method, remember to delete pass
        if user in self.all_tweets:
            self.all_tweets[user]=[tweet]+self.all_tweets[user]
        else:
            self.all_tweets[user]=[tweet]

class User:
    def __init__(self, twitter):
        self.twitter = twitter
        self.my_id = twitter.get_num_users()
        self.twitter.add_user(self.my_id)
        self.following = []
        
    def post_tweet(self, tweet):
        # TODO: Implement this function
        # After you implement the method, remember to delete pass
        user=self.my_id
        self.twitter.add_tweet(user,tweet)
        
    def get_news_feed(self):
        # TODO: Implement this function
        # After you implement the method, remember to delete pass
        return self.twitter.get_tweets(self.following)
        
    
    def follow(self, other):
        self.following.append(other)
        
    def unfollow(self, other):
        if other in self.following:
            self.following.remove(other)

def main():
    my_twitter = Twitter()
    
    user0 = User(my_twitter)
    user0.post_tweet("Hello world!")
    user0.post_tweet("Good morning!")
    user0.post_tweet("Good afternoon!")

    user1 = User(my_twitter)
    user1.post_tweet("Apple")
    user1.post_tweet("Orange")
    user1.post_tweet("Strawberry")
    
    user2 = User(my_twitter)
    user2.post_tweet("New York")
    user2.post_tweet("Shanghai")
    user2.post_tweet("London")
    for i in range(9):
        user2.post_tweet(str(i))

    user0.follow(1)
    user0.follow(2)
    user1.follow(0)

    result0 = user0.get_news_feed()
    result1 = user1.get_news_feed()
    result2 = user2.get_news_feed()
    
    print("\nThe news feed for user 0 is as following:")
    for inner in result0:
        print("User",inner[0],"posted:",inner[1])
        
    print("\nThe news feed for user 1 is as following:")
    for inner in result1:
        print("User",inner[0],"posted:",inner[1])
        
    print("\nThe news feed for user 2 is as following:")
    for inner in result2:
        print("User",inner[0],"posted:",inner[1])

main()
        
