# Infrastructure Technical Skills Assessment 
This is a quick hack bumped out in 4ish hours - would be better with loops and better array management.   
>   "If I had more time, I'd write a shorter letter"   
>     --Someone cool

## What it does:
Currently this code will:
- Deploy a couple subnets to house a database, a couple subnets to house the load balancer, and a couple subnets to house a variable number of nodes managed by an autoscaler. 
- The nodes will display some plain text showing their hostname and the uptime of the database they are connecting to.


## What to do:
  Install pulumi - https://www.pulumi.com/docs/get-started/aws/begin/   
  setup your account at pulumi, it's free.
  ```
  mkdir CraigsTSA
  cd CraigsTSA
  pulumi new https://github.com/yNosGR/TSA.git
    #give it a name if you want, otherwise hit enter a few times
  pulumi up -y
  ```
  due to a S3 policy bug I couldnt work out in a reasonable amount of time, you need to run this twice. It fails with the ELB not being able to write logs to the bucket. Running it a second time fixes it.
  ```
  pulumi up -y
    yes
  ```
  Once the ASG and LB are happy check the elb address listed as an output
  ```
  pulumi destroy
  pulimi stack rm
  ``` 
## What I'd do differently on something bigger than a demo.
- Have a domain in route53 to make a records and certs. This would fix the hardcoding DB in user_data.  
- Put DB passwords in a secret keystore of some sort..  
- Setup user_data to deploy/register puppet/ansible/salt/whatever and deploy the app via SSM.    
- Create another S3 bucket and use that to back cloudfront for static content.    
- Use an ALB rather than a classic elb.   
- ~~Use autoscaling groups to manage the number of instances behind the lb.~~
- Implement a better bucket policy apply method. 
  

