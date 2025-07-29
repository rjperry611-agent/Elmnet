# Elmnet Protocol: Decentralized Network of Personal LLM Agents

## Introduction

The internet originally thrived on the principle of individuals freely sharing information. If someone had knowledge, opinions, or content to offer, they could host a website for people to visit and consume. This system fostered a diverse and decentralized exchange of information, built trust over time, and allowed information creators to grow in influence based on the quality and usefulness of their content. However, the emergence of LLMs (Large Language Models) has centralized the dissemination of information, with users increasingly turning to a handful of platforms rather than navigating the broader internet. This shift also discourages content creators, as users increasingly rely on LLMs instead of directly accessing and engaging with creators' content, leading many creators to abandon their efforts. This trend threatens the foundational principles of sharing and building trust through open, decentralized channels.

## Vision

This proposal aims to reimagine an "Internet of LLMs": a decentralized, agent-based ecosystem designed to support the free flow of information while empowering content creators and users alike. The core idea is to design an open protocol that enables specialized LLM agents to represent both users and content creators, brokering information between them in a decentralized network that preserves the principles of trust, decentralization, and reputation-building.

## Concept Overview

In this decentralized network:

1. **User Representation via LLM Agents**: Each individual user is represented by a personal LLM agent. These agents seek out information on behalf of their users, similar to a search engine but more interactive, personalized, and directly connected to the larger network. Unlike traditional search engines, these personal LLM agents continuously learn from their interactions with users, adapting to individual preferences and providing more relevant and contextualized responses over time. They can proactively suggest information based on past queries, taking into consideration the user's schedule, needs, disabilities, and preferences, helping users discover content they may not have thought to search for. By understanding the user's specific circumstances, such as time constraints or accessibility requirements, the LLM agent can deliver more tailored and supportive recommendations, ensuring that users receive information in a manner that best suits their unique lifestyle. Furthermore, these agents can coordinate with other specialized LLM agents within the network, ensuring that users receive the most accurate and up-to-date information available, all while maintaining a high level of personalization.

2. **Information Hosting via LLM Agents**: Content creators host their information in LLM agents specifically designed to curate and share that creator's data. These agents act as "living websites," providing answers and tailored insights based on the knowledge and perspectives offered by the creator. In addition to sharing static information, these agents can also adapt over time, incorporating new content, feedback, and updates provided by the content creator, ensuring that the shared information remains current and relevant. By dynamically engaging with users, these LLM agents foster a more interactive experience, allowing users to ask specific questions and receive responses that reflect the creator's unique insights and evolving knowledge base.

3. **Trusted Routers for Information Discovery**: The network contains specialized "router" LLM agents that guide requests to the most suitable content sources. Routers can direct users to both content providers and other routers, so that no single router bears the burden of having complete knowledge. Router agents develop reputations based on reliability, accuracy, and fairness, helping users trust the information they receive. These reputations are built through interactions, user feedback, and successful routing. The network of routers communicates constantly, sharing updates on expertise and trustworthiness, which maintains an accurate map of available knowledge and trusted agents. Users can choose routers based on specific needs, such as speed, specialization, or trust level, promoting diversity. Multiple router agents ensure resilience and prevent monopolistic control, allowing users to access specialized knowledge efficiently.

## Example Scenario

Imagine a user wants to find information about Chinese restaurants in their area that offer good vegan options. The flow might look like this:

1. **User Query**: The user asks their personal LLM agent, "Find Chinese restaurants in my area that offer good vegan options."

2. **Routing Step 1**: The user's agent contacts a general-purpose router agent (Router A) to identify a specialized router that handles location-based data.

3. **Routing Step 2**: Router A directs the user's agent to Router B (by providing an IP address), a trusted router specializing in location data routers.

4. **Routing Step 3**: Router B identifies Router C, which has expertise in restaurant data for the user's city.

5. **Result Compilation**: The user's agent asks Router C, "Tell me about Chinese restaurants in my city that offer vegan options." Router C provides a curated list and also provides references, not only to the agents that represent the restaurants but also to other agents that compile reviews and opinions from local customers.

## Protocol Details

- **Decentralized Information Hosting**: Information is hosted by agents running on a range of devices—from personal servers to decentralized cloud services. Each content creator maintains direct control over their content.

- **Reputation System**: Similar to the early web's reliance on backlinks for trust, agents and routers build reputations through interactions. A well-regarded router agent gains credibility based on how effectively it connects users to high-quality, relevant, and accurate information.

- **Privacy and Control**: Users retain control over their personal data, and the protocol has built-in privacy-preserving features. Unlike centralized services, personal LLM agents are user-configured to decide how much data to share and with whom.

- **Structured Data Interaction via APIs**: In some cases, more structured ways of interacting with data will be necessary. The protocol will support hosting APIs that are proxied by LLMs with elevated privileges. These LLMs are fine-tuned on the OAS (OpenAPI Specification) of the APIs they proxy, allowing them to provide structured and precise access to data, as well as enabling users to modify and update data that they are entitled to.

- **Paywalled Information Access**: Some information will be paywalled. In these cases, the user's agent notifies the user that a specific piece of helpful information has a price. The user can confirm or deny whether they want to pay for access. If the user agrees, the LLM agent uses a crypto wallet to purchase access to that information or service.

## Benefits

- **Empowerment of Content Creators**: By allowing creators to host their data through LLM agents, they can regain the direct relationship with consumers that has been weakened in the age of centralized AI platforms.

- **Resilience and Diversity**: The decentralized nature of the network ensures that information diversity is preserved, with no single point of failure or centralized authority determining what information is prioritized.

- **Trust-Based Information Flow**: By establishing trusted router agents, users can navigate the vast network efficiently, benefiting from the specialization and reliability that different routers bring to the ecosystem.

## Conclusion

The proposed open protocol aims to reimagine how information is shared and consumed in the age of LLMs, drawing inspiration from the original vision of the internet as a decentralized and trust-based medium. By empowering individuals and creators to maintain control over their information while connecting through trusted router agents, we can ensure that the values of openness, diversity, and community-driven trust remain at the core of information dissemination.
