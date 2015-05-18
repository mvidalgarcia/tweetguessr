from tweetguessr.tweetguessr import TweetGuessr

args = vars(TweetGuessr.parse_arguments())
tweetguessr = TweetGuessr(args)
tweetguessr.main(args)
