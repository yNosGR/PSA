This is a quick low energy hack - would be better with loops and better array management.
   "If I had more time, I'd write a shorter letter"
     --Someone cool

What to do:
  clone repo
  Install pulumi - https://www.pulumi.com/docs/get-started/install/
  pulumi up
  # due to a S3 policy bug I couldnt work out in a reasonable amount of time, you need to run this twice.
  pulumi up
  # play
  # check the elb address listed as an output
  pulumi destroy
  
### What I'd do differently on something bigger than a demo.
have a domain in route53 to make a records and certs. 
put passwords and ssh keys in a secret store of some sort.. Or skip the ssh keys and just use ssm console for puppet/ansible/whatever.
create another S3 bucket and use that to back cloudfront for static content.
use an ALB rather than a classic elb. trying to stick to free tier here.
Implement a better bucket policy apply method.



