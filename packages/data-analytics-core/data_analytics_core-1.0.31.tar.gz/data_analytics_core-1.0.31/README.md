<h1>DA Core</h1>
<h2>RTFM</h2>
⚛️ <b>This repo is meant to have all the globally shared modules in all Data-Analytics.</b> ⚛️

Works with python 3.9 and higher. 💪

⚛️

To install this package 💯 , paste in the console:

 <code>pip3 install --upgrade data-analytics-core</code> 

⚛️

<summary><h2>Steps to install and use the LocalStack module of this repo</h2></summary><blockquote>
    <details><summary>I- List of previous dependencies</summary>
        <ol>
        <li><a href="https://brew.sh/">Brew</a></li>
        <li><a href="https://docs.docker.com/desktop/install/mac-install/">Docker Desktop</a></li>
        <li>Download <a href="https://www.python.org/downloads/release/python-3916/">Python 3.9.16</a></li>
        </ol>
    </details>
    <details><summary>II- LocalStack</summary>
        To be able to use LocalStack docker instances, execute:
        <br><code>pip install localstack</code>
        <br>Then use (if you don't own a PRO account of LS):
        <br><code>docker image pull localstack/localstack:0.14.2</code>
        <br>Else use:
        <br><code>docker image pull localstack/localstack-pro:3.2.0</code>
        <br>You can also use a specific LS big data image (try the<code>latest-bigdata</code> version for cool stuff testing) or any other version of your will 
    </details>
    <details><summary>III- Extra Info</summary>
        <ol>
        Before starting, open docker desktop and initialize (run) a container of the LS image.
        It is usually called <code>AWSLocalStackMock</code>
        <br>Keep in mind that if you are willing to use a pro version, you'll need to state an environment variable called:
        <br><code>LOCALSTACK_AUTH_TOKEN</code> filled with your personal LS PRO token.
        </ol>
    </details>
  </blockquote>

⚛️

[!IMPORTANT] For AWS :cloud: users, we strongly recommend to install it with its dependencies, 
yet if you are deploying it inside an AWS Layer, you should make sure it has the max size boundaries from the AWS cloud,
or deploy it in a Layer cluster that includes all its dependencies, while using the flag 
<code>--no-deps</code> in the pip command. 🧑‍🔧

⚛️

For any contribution [PR](https://github.com/seatcode/data-analytics-core/pulls) 🧑‍💻, reference, 
issue, version upgrade convention or question, you can ask to any of the Authors, open an issue or
 ask directly to ⚜️@MarcVea⚜️️
Also, you can look for any further info in the [wiki](https://github.com/seatcode/data-analytics-core/wiki), 
look for the [issues](https://github.com/seatcode/data-analytics-core/issues) and their status, or open any [discussion](https://github.com/seatcode/data-analytics-core/discussions) you might need.

⚛️
