# ExtraUtils
25.07.2025: modified asyncTokens now asyncKeys (ansyncronus en- and decryption)
will provide a bunch of small functionalities to speedup development.

(In active development, so if you have any suggestions, to make other developers life easier, feel free to submit them.)

# Latest addition

### TimeBasedToken()
Generates a time-based token using two keys: a primary and a secondary. Ideal for encrypting traffic between devices or services without sharing the actual tokens.

**How it works:**
- Utilizes a unified timestamp, rounded to the nearest tenth of a second.
- Uses the primary token as is.
- Applies a transformation to the secondary token for added security.

**Example:**
```py
primary = "1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p"
secondary = "7q8r9s0t1u2v3w4x5y6z7a8b9c0d1e2f"
def main():
    final_token = TimeBasedToken(primary, secondary)

    print(final_token.regenerate())
    enc = final_token.encrypt("Hello World, i am going to be encrypted and decrypted again. : )")
    print(enc)
    dec = final_token.decrypt(enc)
    print(dec)

if __name__ == "__main__":
    main()
```

### RateLimiter()
Limits the rate of operations to prevent overloading. Configurable thresholds, decay rates, and behaviors on limit reaching.

**Example**
```py
# A very simplified example
from ExtraUtils import RateLimiter
rate_limit = RateLimiter(10,15,5,1,True)
# threshold (10) -> increments before rate_limit.hit is set to True
# upperCap (15) -> the highest value the trigger counter will go
# decay_rate (5) -> the amount in triggers to be decremented each decay cycle
# decay_time (1) -> the time in seconds between each decay cycle
# extreme_case (True) -> if an exeption should be raised (if True) or just rate_limit.hit set to True (if False)

def rate_limit_test(i:int):
    rate_limit.increment()
    print(i,rate_limit.hit)

for i in range(20):
    rate_limit_test(i)

# Output:	
#0 False
#(1 to 8) False
#9 False
#Traceback (most recent call last):
#  File "E:\Developement\RTS-Modules\ExtraUtils\showcase.py", line 14, in <module>
#    rate_limit_test(i)
#  File "E:\Developement\RTS-Modules\ExtraUtils\showcase.py", line 5, in rate_limit_test
#    rate_limiter.increment()
#  File "E:\Developement\RTS-Modules\ExtraUtils\ExtraUtils\RateLimit.py", line 30, in increment
#    raise RateLimited()
#ExtraUtils.RateLimit.RateLimited: Rate limit reached
```
Aditional methods are:
```py
RateLimiter().pause_decay()
RateLimiter().resume_decay()
```
