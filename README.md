# Kenkyu - Free Deep Research on Local

## High level overview steps

1. User gives intent of the deep research.
2. Hit LLM and generate few questions to clarify more.
    a. Use this https://arxiv.org/pdf/2406.12639
    b. Refer this: https://github.com/magicgh/Ask-before-Plan
3. User answers the clarifying questions.
4. Plan the steps to do deep research.
    a. What to search on the internet? Keywords to search.
    b. How to classify something as useful content?
5. Use Google / Free web search / Serper / Yahoo / Duck Duck Go for web search.
6. Collect all the information (Links to be researched)
7. Research individual links, gather all the relevant information from the link, summarize and store it SOMEWHERE(Graph DB, Vector DB?)
8. Provide and detailed final response gathering all the information so far.
    a. How to collate everything nicely (Big problem alone to be solved)
9. 


## Performance Results

Minimum specifications required for better performance. Optimize and slow down if the laptop doesn't support. Adjust research according to the laptop - local specifications.

1. Macbook Silicon - Speed, Memory, CPU.


## Future scope: Online scaling

1. Put all of these in Kubernetes cluster.
2. Run all of these as parallel jobs to scrape and extract content from the Internet.
