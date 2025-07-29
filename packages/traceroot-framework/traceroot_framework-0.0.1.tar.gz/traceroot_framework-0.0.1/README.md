<div align="center">
  <a href="https://traceroot.ai/">
    <img src="misc/images/banner.svg" alt="Banner" width="80%">
  </a>
</div>

<div align="center">

[![Documentation][docs-image]][docs-url]
[![Discord][discord-image]][discord-url]
[![PyPI Version][pypi-image]][pypi-url]
[![PyPI SDK Downloads][pypi-sdk-downloads-image]][pypi-sdk-downloads-url]
[![TraceRoot.AI Website][company-website-image]][company-website-url]
[![X][company-x-image]][company-x-url]
[![LinkedIn][company-linkedin-image]][company-linkedin-url]
[![WhatsApp][company-whatsapp-image]][company-whatsapp-url]

</div>


<div align="center">
<h4 align="center">

[Contributing](CONTRIBUTING.md) |
[TraceRoot.AI](https://traceroot.ai/) |
[Community](https://discord.gg/CeuqGDQ58q/) |
[SDK](https://github.com/traceroot-ai/traceroot-sdk) |
[Documentation](https://docs.traceroot.ai)

</h4>

Join us ([*Discord*](https://discord.gg/CeuqGDQ58q/)) in pushing the boundaries of debugging with AI agents. 

Please 🌟 Star TraceRoot on GitHub and be instantly notified of new releases.
</div>

## TraceRoot Framework Design Principles

<h3>🤖 Intelligence</h3 >

The framework enables multi-agent systems to continuously evolve by interacting with environments.

<h3>⏰ Real-Time</h3 >

The framework enables real-time tracing and logging to your applications.

<h3>🧠 Structured Information</h3 >

The framework enables utilizing structured loggings and tracing data to improve the performance of AI agents.

<h3>💻 Integration</h3 >

The framework enables integrating with other sources and tools, such as GitHub, Notion, etc. This provides a seamless experience for you to use the framework in your applications.

<h3>😊 Developer Friendly</h3 >

We provide a Cursor like interface but specialized for debugging and tracing. You can select the logs and traces you are interested in and ask the framework to help you with the analysis.

## Why Use TraceRoot for Your Applications?

We are a community-driven collective comprising over multiple engineers and researchers dedicated to advancing frontier engineering and research in using Multi-Agent Systems to help not only human but also AI agents on debugging, tracing, and root cause analysis.

<table style="width: 100%;">

  <tr>
    <td align="left">✅</td>
    <td align="left" style="font-weight: bold;">Multi-Agent System</td>
    <td align="left">Multi-Agent system that can be used to solve complex tasks.</td>
  </tr>
  <tr>
    <td align="left">✅</td>
    <td align="left" style="font-weight: bold;">Real-Time Tracing and Logging</td>
    <td align="left">Enable real-time tracing and logging to your applications.</td>
  </tr>
  <tr>
    <td align="left">✅</td>
    <td align="left" style="font-weight: bold;">Structured Logging</td>
    <td align="left">Enable structured logging to your applications, which allows better performance of AI agents.</td>
  </tr>
  <tr>
    <td align="left">✅</td>
    <td align="left" style="font-weight: bold;">Integration with Multiple Resources</td>
    <td align="left">Integrate with other sources and tools, such as GitHub, Notion, etc.</td>
  </tr>
  <tr>
    <td align="left">✅</td>
    <td align="left" style="font-weight: bold;">Developer Friendly</td>
    <td align="left">We provide a Cursor like interface but specialized for debugging and tracing.</td>
  </tr>
</table>

## Installation

You can install the latest version of TraceRoot with the following command:

Or you can install the latest version of TraceRoot with the following command:

Install the dependencies locally:

```bash
python3.11 -m venv venv
source venv/bin/activate
pip install .
# Or
pip install -e .
```

## Local Usage

You can use the TraceRoot framework locally by following the [README.md in the `ui` directory](ui/README.md) and [README.md in the `rest` directory](rest/README.md).

Also, you can build the docker image and run the docker container by following the [README.md in the `docker` directory](docker/public/README.md).

Or even simpler, just pull the docker image by

```bash
docker pull zechengzh/traceroot-public:v0.0.1
docker run -d --name traceroot-public -p 3000:3000 -p 8000:8000 zechengzh/traceroot-public:v0.0.1
```

This will start the UI at [http://localhost:3000](http://localhost:3000) and the API at [http://localhost:8000](http://localhost:8000).

Before using the TraceRoot framework, you need to setup the Jaeger docker container at first. It will be used to store the traces and logs and capture the traces and logs from our SDK integrated with your applications.

```bash
docker run -d --name jaeger \
  -e COLLECTOR_OTLP_ENABLED=true \
  -p 16686:16686 \
  -p 14268:14268 \
  -p 14250:14250 \
  -p 4317:4317 \
  -p 4318:4318 \
  cr.jaegertracing.io/jaegertracing/jaeger:2.8.0
```

## SDK

Our platform is built on top of the TraceRoot SDK. You need to use our SDK to integrate with your applications by

```bash
pip install traceroot==0.0.4a5
```

To use the local mode of the TraceRoot SDK, you need create a `.traceroot-config.yaml` file in the root directory of your project with following content:
```yaml
local_mode: true
service_name: "your-service-name"
github_owner: "your-github-owner"
github_repo_name: "your-github-repo-name"
github_commit_hash: "your-github-commit-hash"
```

As mentioned above, you need to setup the Jaeger docker container at first before let the TraceRoot SDK capture the traces and logs from your applications.

For more details or the SDK usage and examples, please checkout this [Quickstart](https://docs.traceroot.ai/quickstart).

[docs-image]: https://img.shields.io/badge/Documentation-0dbf43
[docs-url]: https://docs.traceroot.ai
[discord-url]: https://discord.gg/CeuqGDQ58q/
[discord-image]: https://img.shields.io/discord/1395844148568920114?logo=discord&labelColor=%235462eb&logoColor=%23f5f5f5&color=%235462eb
[pypi-image]: https://badge.fury.io/py/traceroot.svg
[pypi-url]: https://pypi.python.org/pypi/traceroot
[company-website-image]: https://img.shields.io/badge/TraceRoot.AI-148740
[company-website-url]: https://traceroot.ai
[company-x-url]: https://x.com/TracerootAI
[company-x-image]: https://img.shields.io/twitter/follow/TracerootAI?style=social
[company-linkedin-url]: https://www.linkedin.com/company/traceroot-ai/
[company-linkedin-image]: https://custom-icon-badges.demolab.com/badge/LinkedIn-0A66C2?logo=linkedin-white&logoColor=fff
[company-whatsapp-url]: https://chat.whatsapp.com/GzBii194psf925AEBztMir
[company-whatsapp-image]: https://img.shields.io/badge/WhatsApp-25D366?logo=whatsapp&logoColor=white
[pypi-sdk-downloads-image]: https://img.shields.io/pypi/dm/traceroot
[pypi-sdk-downloads-url]: https://pypi.python.org/pypi/traceroot