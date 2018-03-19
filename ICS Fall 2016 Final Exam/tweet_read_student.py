import random

class Dice:
    def __init__(self, bias=0.5):
        self.bias = bias

    def roll(self):
        return random.uniform(0, 1) < self.bias

class Tweet:
    def __init__(self, interest=0.5):
        self.d = Dice(interest)

    # if interest = 0.1, then 10% of the tweets are interesting
    def gen_interest(self):
        return self.d.roll()

if __name__ == "__main__":
    # fix seed for reprousability
    random.seed(0)

    # the dice to decide when to explore and when to exploit
    epsilon = 0.1
    player_dice = Dice(epsilon)

    # the true intrestingness of the twitters
    interests = [0.1, 0.6, 0.4]
    num_twitters = len(interests)
    twitters = []
    for i in range(num_twitters):
       m = Tweet(interests[i])
       twitters.append(m)

    # assign fair (but wrong) estimation
    my_feeds = {}
    warm_up = 100
    for i in range(num_twitters):
        my_feeds[i] = {}
        my_feeds[i]['likes'] = float(warm_up/2)
        my_feeds[i]['reads'] = warm_up

    print("+++++++ initial feeds")
    for i in range(num_twitters): print(my_feeds[i])
    print("------- ground truth interests: ")
    print(interests)

    # makes num_reads bigger (e.g. 1000000) gives better
    # results (as in the exam sheet). 
    num_reads = 100000

    # IMPLEMENT THE FOLLOWING PART
    # the variable "pick" is the account your algorithm will
    # select in each round. 
    # likes/reads gives the estimated interest rate
    for i in range(num_reads):
        # COMMENT OUT the following line and implement e-greedy
        pick = 0
        if player_dice.roll():
            pick=random.randint(0,2)
        else:
            max_index=0
            max_interest=my_feeds[0]['likes']/my_feeds[0]['reads']
            for i in range(num_twitters):
                if my_feeds[i]['likes']/my_feeds[i]['reads']>max_interest:
                    max_index=i
                    max_interest=my_feeds[i]['likes']/my_feeds[i]['reads']
            pick=max_index

        # explore to select the "pick"
                
        # exploit to select the "pick"

        # DON'T HAVE TO CHANGE THE FOLLOWING 2 LINES
        my_feeds[pick]['reads'] += 1
        my_feeds[pick]['likes'] += twitters[pick].gen_interest()

    print("\n")
    print("++++++++ after reading ", num_reads)
    for i in range(num_twitters): print(i, my_feeds[i])
    print("-------- estimated interests")
    for i in range(num_twitters):
        print(i, my_feeds[i]['likes']/my_feeds[i]['reads'])
