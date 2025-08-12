# **🤖 LLM Quality & Security Framework: A Learning Journey 🚀**

Welcome\! This project is a chronicle of my deep dive into AI Quality Engineering, undertaken as a self-directed learning initiative during a career transition. It's a **work-in-progress** that documents the real-world process of building a complex testing framework, tackling challenging bugs, and learning new technologies from the ground up.

The goal is to create a robust, multi-provider framework for the automated red teaming of Large Language Models from providers like **Google (Gemini)**, **OpenAI (GPT)**, **Anthropic (Claude)**, and **xAI (Grok)**.

## **✨ Key Features & Skills Demonstrated**

This framework, while still under development, successfully integrates several key technologies and showcases a range of QE skills:

* **🌐 Multi-Provider Testing**: A flexible API client capable of interfacing with multiple, distinct LLM provider APIs.  
* **⚔️ Hybrid Attack Scenarios**: Orchestrates tests using both the deepteam library's built-in attacks and custom, user-defined prompts from .yaml files.  
* **💾 Persistent Data Logging**: A modular SQLite logger that captures detailed results from every test case, creating a rich dataset for analysis.  
* **📊 Interactive Data Visualization**: A standalone Python script that uses **pandas** and **PyGWalker** to launch an interactive, Tableau-like dashboard for exploring the test data.  
* **🤖 Robust Orchestration**: Leverages the **Robot Framework** to define and manage complex test suites, demonstrating skills in building scalable and maintainable test automation.

## **🗺️ The Journey So Far: A QE's Problem-Solving Log**

This project has been an incredible learning experience, marked by the kind of challenges that define modern software quality assurance.

#### **1\. The Pivot: Adapting to Roadblocks**

The initial plan hit a wall due to dependency conflicts with other libraries. The first key learning was knowing when to pivot. I made the strategic decision to integrate the deepteam library, which required adapting my existing codebase to its asynchronous nature.

#### **2\. The Learning Curve: Embracing asyncio**

deepteam's reliance on Python's asyncio was a fantastic opportunity to learn a new programming paradigm. The journey involved:

* Refactoring synchronous code to be async-native.  
* Debugging subtle but critical TypeError and RuntimeWarning exceptions related to un-awaited coroutines.  
* **Key Takeaway**: Understanding how orchestration layers can sometimes mask the root cause of errors, reinforcing the importance of isolated component testing.

#### **3\. The "Silent Failure": A Deep Dive into Debugging**

The most challenging phase was a "silent failure" mode where tests would appear to pass but no real work was being done. My investigation followed a systematic QE process:

* **Hypothesis 1: Environment Issues.** I discovered the subprocess wasn't inheriting API keys. **Solution:** I engineered a more robust solution using a .env file and python-dotenv, a best practice for managing secrets.  
* **Hypothesis 2: I/O Buffering.** I realized the subprocess was hiding terminal output. **Solution:** I modified the subprocess call to force unbuffered I/O, a deep dive into process management.

## **🚀 Current Status & The Next Challenge**

This branch is a testament to a journey of learning and perseverance. It's a feature-rich framework that is one major step away from being fully operational.

* **✅ What's Working:** The API clients, Robot Framework orchestration, the SQLite database logger, and the PyGWalker visualization dashboard are all built and functional.  
* **🚧 The Current Blocker:** The framework is currently blocked by a persistent pydantic ValidationError related to an un-awaited coroutine. This is the final puzzle to solve in the deepteam integration.  
* **🎯 The Path Forward:** The immediate next step is to apply the lessons learned from this debugging journey to resolve this final async issue. This will unlock the full potential of the framework and complete this chapter of my self-directed learning in AI Quality Engineering.