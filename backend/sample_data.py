"""
Fictional candidate sample data and sample job descriptions.
Demonstrates dual capability in Software Development (Python/Backend) and Network Engineering.
"""

SAMPLE_PROFILE = {
    "full_name": "Alex Morgan",
    "headline": "Junior Backend Developer & Network Infrastructure Specialist",
    "email": "alex.morgan@example.com",
    "phone": "+1 (555) 019-2834",
    "location": "Seattle, WA",
    "github_url": "https://github.com/alexmorgan-dev",
    "linkedin_url": "https://linkedin.com/in/alexmorgan-tech",
    "portfolio_url": "https://alexmorgan.dev",
    "summary": "Versatile Computer Science graduate with hands-on background in both backend systems development and enterprise network administration. Proven track record building resilient REST APIs with Python/Flask/PostgreSQL and designing robust, secure TCP/IP network topologies (VLANs, routing protocols, packet analysis). Passionate about systems reliability, clean architecture, and infrastructure automation."
}

SAMPLE_EDUCATION = [
    {
        "institution": "University of Washington",
        "degree": "Bachelor of Science",
        "field_of_study": "Computer Science & Networking (Minor in Mathematics)",
        "start_date": "2021-09",
        "end_date": "2025-06",
        "gpa": "3.82 / 4.00",
        "description": "Relevant Coursework: Distributed Systems, Computer Networks, Database Internals, Operating Systems, Data Structures & Algorithms, Network Security.",
        "order_index": 1
    }
]

SAMPLE_SKILLS = [
    # Languages & Backend
    {"name": "Python", "category": "Languages", "proficiency": "Expert", "years_of_experience": 3.0},
    {"name": "SQL", "category": "Languages", "proficiency": "Advanced", "years_of_experience": 2.5},
    {"name": "Bash/Shell", "category": "Languages", "proficiency": "Intermediate", "years_of_experience": 2.0},
    {"name": "JavaScript", "category": "Languages", "proficiency": "Intermediate", "years_of_experience": 1.5},
    {"name": "Flask", "category": "Backend & APIs", "proficiency": "Advanced", "years_of_experience": 2.5},
    {"name": "FastAPI", "category": "Backend & APIs", "proficiency": "Intermediate", "years_of_experience": 1.5},
    {"name": "RESTful APIs", "category": "Backend & APIs", "proficiency": "Advanced", "years_of_experience": 2.5},
    {"name": "JWT Authentication", "category": "Backend & APIs", "proficiency": "Intermediate", "years_of_experience": 2.0},
    {"name": "PostgreSQL", "category": "Databases", "proficiency": "Advanced", "years_of_experience": 2.5},
    {"name": "SQLite", "category": "Databases", "proficiency": "Advanced", "years_of_experience": 3.0},
    {"name": "Redis", "category": "Databases", "proficiency": "Intermediate", "years_of_experience": 1.5},
    
    # Networking & Protocols
    {"name": "TCP/IP", "category": "Networking & Protocols", "proficiency": "Expert", "years_of_experience": 3.0},
    {"name": "Subnetting", "category": "Networking & Protocols", "proficiency": "Expert", "years_of_experience": 3.0},
    {"name": "VLANs", "category": "Networking & Protocols", "proficiency": "Advanced", "years_of_experience": 2.5},
    {"name": "Routing & Switching", "category": "Networking & Protocols", "proficiency": "Advanced", "years_of_experience": 2.5},
    {"name": "OSPF", "category": "Networking & Protocols", "proficiency": "Advanced", "years_of_experience": 2.0},
    {"name": "DNS & DHCP", "category": "Networking & Protocols", "proficiency": "Advanced", "years_of_experience": 2.5},
    {"name": "Wireshark", "category": "Networking & Protocols", "proficiency": "Advanced", "years_of_experience": 2.5},
    {"name": "Network Troubleshooting", "category": "Networking & Protocols", "proficiency": "Expert", "years_of_experience": 3.0},

    # Tools & DevOps
    {"name": "Git", "category": "DevOps & Tools", "proficiency": "Expert", "years_of_experience": 3.0},
    {"name": "GitHub", "category": "DevOps & Tools", "proficiency": "Advanced", "years_of_experience": 3.0},
    {"name": "Docker", "category": "DevOps & Tools", "proficiency": "Intermediate", "years_of_experience": 1.5},
    {"name": "Linux (Ubuntu/Debian)", "category": "DevOps & Tools", "proficiency": "Advanced", "years_of_experience": 3.0},
    {"name": "Postman", "category": "DevOps & Tools", "proficiency": "Advanced", "years_of_experience": 2.5},
    {"name": "Cisco Packet Tracer", "category": "DevOps & Tools", "proficiency": "Advanced", "years_of_experience": 2.5}
]

SAMPLE_CERTIFICATIONS = [
    {
        "name": "Cisco Certified Network Associate (CCNA 200-301)",
        "issuing_organization": "Cisco",
        "issue_date": "2024-10-15",
        "expiration_date": "2027-10-15",
        "credential_id": "CCNA-884920",
        "credential_url": "https://www.credly.com/org/cisco/badges"
    },
    {
        "name": "Certified Associate in Python Programming (PCAP)",
        "issuing_organization": "Python Institute",
        "issue_date": "2024-03-20",
        "expiration_date": "",
        "credential_id": "PCAP-31-03",
        "credential_url": "https://pythoninstitute.org/certification"
    },
    {
        "name": "AWS Certified Cloud Practitioner",
        "issuing_organization": "Amazon Web Services",
        "issue_date": "2025-01-10",
        "expiration_date": "2028-01-10",
        "credential_id": "AWS-CCP-7193",
        "credential_url": "https://aws.amazon.com/verification"
    }
]

SAMPLE_PROJECTS = [
    {
        "title": "Distributed Task Queue & REST API Platform",
        "description": "A high-performance asynchronous task orchestration system and RESTful API built for distributed batch workloads.",
        "tech_stack": '["Python", "Flask", "Redis", "PostgreSQL", "Docker", "Git"]',
        "role": "Lead Backend Developer",
        "highlights": '[ "Architected RESTful endpoints handling 1,500+ requests/sec using Flask, PostgreSQL, and connection pooling.", "Implemented asynchronous background job workers with Redis queues, backoff retry logic, and real-time execution state monitoring.", "Enforced token-based JWT authentication, rate limiting, and strict input schema validation.", "Created automated test suites using pytest with 92% code coverage and integrated CI workflows." ]',
        "live_url": "https://taskqueue.demo.alexmorgan.dev",
        "repo_url": "https://github.com/alexmorgan-dev/distributed-task-queue",
        "start_date": "2024-02",
        "end_date": "2024-06"
    },
    {
        "title": "Cloud Microservices API Gateway & Database Service",
        "description": "Centralized API gateway routing and caching microservice requests with relational data storage.",
        "tech_stack": '["Python", "FastAPI", "SQLite", "SQL", "Docker", "REST APIs"]',
        "role": "Backend Developer",
        "highlights": '[ "Constructed API gateway with dynamic request routing, circuit breaker patterns, and in-memory caching.", "Optimized relational database queries, schema indices, and transactions, cutting p99 response times by 35%.", "Dockerized the application for multi-stage production deployment." ]',
        "live_url": "",
        "repo_url": "https://github.com/alexmorgan-dev/microservices-gateway",
        "start_date": "2024-07",
        "end_date": "2024-10"
    },
    {
        "title": "Enterprise Campus Network & VLAN Topology",
        "description": "Multi-tier campus network architecture simulated with redundant links, segmented subnets, and robust access controls.",
        "tech_stack": '["Cisco Packet Tracer", "VLANs", "OSPF", "Subnetting", "TCP/IP", "Wireshark"]',
        "role": "Network Architecture Lead",
        "highlights": '[ "Engineered a redundant 3-tier enterprise network topology serving 1,200 users across 8 departmental VLANs (802.1Q).", "Configured multi-area OSPF routing, inter-VLAN routing on Layer 3 Catalyst switches, and port security.", "Implemented network access control lists (ACLs), DHCP snooping, and dynamic ARP inspection to prevent unauthorized spoofing.", "Analyzed Wireshark packet captures to evaluate latency and eliminate broadcast loops." ]',
        "live_url": "",
        "repo_url": "https://github.com/alexmorgan-dev/campus-network-topology",
        "start_date": "2023-10",
        "end_date": "2024-01"
    },
    {
        "title": "Real-Time Packet Sniffer & Traffic Diagnostic Tool",
        "description": "Lightweight Linux network diagnostics CLI analyzing raw socket payloads, IP headers, and detecting anomalous traffic.",
        "tech_stack": '["Python", "TCP/IP", "Wireshark", "Linux", "Socket Programming", "Troubleshooting"]',
        "role": "Systems Developer",
        "highlights": '[ "Developed a low-overhead Python CLI utilizing raw sockets to dissect IPv4, TCP, UDP, and ICMP frame headers in real time.", "Built rule-based detection for SYN flood attacks and unauthorized DHCP servers on local subnets.", "Awarded 2nd Place in the UW Systems Engineering & Cybersecurity Hackathon." ]',
        "live_url": "",
        "repo_url": "https://github.com/alexmorgan-dev/py-traffic-sniffer",
        "start_date": "2024-03",
        "end_date": "2024-05"
    }
]

SAMPLE_EXPERIENCE = [
    {
        "company": "TechNova Systems",
        "role": "Backend Engineering Intern",
        "location": "Seattle, WA",
        "start_date": "2024-06",
        "end_date": "2024-09",
        "is_current": False,
        "description": "Developed backend microservices and database query layers for an enterprise analytics dashboard.",
        "highlights": '[ "Developed RESTful API endpoints in Python using Flask and PostgreSQL, reducing endpoint response times by 28%.", "Collaborated with senior engineers using Git version control, branch workflows, and code reviews.", "Authored integration tests with pytest, ensuring data integrity across complex financial ledger mutations.", "Containerized local development workflows using Docker." ]'
    },
    {
        "company": "Campus IT Services (University of Washington)",
        "role": "Network Support & Infrastructure Specialist",
        "location": "Seattle, WA",
        "start_date": "2023-09",
        "end_date": "2024-05",
        "is_current": False,
        "description": "Maintained and troubleshot campus-wide enterprise network infrastructure serving over 15,000 active endpoints.",
        "highlights": '[ "Resolved 200+ Tier-2 network connectivity tickets involving DHCP exhaustion, DNS misconfigurations, and VLAN tagging issues.", "Configured Cisco switches and wireless access points via CLI; verified subnet routing and trunk ports.", "Conducted on-site packet captures using Wireshark to diagnose packet loss and high TCP retransmission rates.", "Documented network topology diagrams and standard operating procedures (SOPs) for incident resolution." ]'
    }
]

SAMPLE_ACHIEVEMENTS = [
    {
        "title": "2nd Place Winner — UW Systems & Cybersecurity Hackathon",
        "type": "Award",
        "issuer_or_publisher": "University of Washington",
        "date": "2024-10",
        "description": "Developed real-time network packet inspection and anomaly detection tool evaluated by industry judges.",
        "url": "https://cs.uw.edu/hackathon/2024-winners"
    },
    {
        "title": "Co-Author: 'Evaluating Latency Trade-offs in Lightweight Edge Task Brokers'",
        "type": "Publication",
        "issuer_or_publisher": "UW Undergraduate Research Symposium",
        "date": "2024-05",
        "description": "Published research paper evaluating message queue throughput and network latency under simulated bandwidth constraints.",
        "url": "https://digital.lib.washington.edu/research/2024"
    },
    {
        "title": "Dean's List for Academic Excellence",
        "type": "Honor",
        "issuer_or_publisher": "UW College of Engineering",
        "date": "2021 - 2024",
        "description": "Recognized for maintaining cumulative GPA above 3.8 across six consecutive academic terms.",
        "url": ""
    }
]

SAMPLE_JOB_DESCRIPTIONS = [
    {
        "title": "Junior Backend Developer",
        "company": "PayFlow FinTech Systems",
        "target_role": "Junior Backend Developer",
        "raw_text": """Position: Junior Backend Developer
Company: PayFlow FinTech Systems
Location: Seattle, WA (Hybrid)

About the Role:
We are seeking a talented and motivated Junior Backend Developer to join our core engineering team. In this role, you will help design, build, and maintain high-volume RESTful APIs and backend services that power financial transactions.

Key Responsibilities:
- Design, implement, and maintain REST APIs using Python (Flask or FastAPI).
- Write efficient SQL queries, manage database schema migrations, and work with relational databases (PostgreSQL or SQLite).
- Collaborate with frontend engineers to integrate API contracts.
- Implement secure authentication, authorization, and input validation.
- Participate in code reviews, write unit and integration tests using pytest, and maintain clean Git history.
- Assist with containerization and deployment using Docker.

Qualifications & Skills:
- Solid programming skills in Python.
- Proven experience designing and building RESTful APIs.
- Strong knowledge of SQL and relational database concepts.
- Familiarity with version control using Git and GitHub.
- Experience with Docker, Redis, or asynchronous queues is a strong plus.
- Bachelor's degree in Computer Science or equivalent practical experience.
- Strong problem-solving skills and eagerness to learn in a fast-paced environment."""
    },
    {
        "title": "Network Support Engineer",
        "company": "GlobalNet Infrastructure Solutions",
        "target_role": "Network Support Engineer",
        "raw_text": """Position: Network Support Engineer
Company: GlobalNet Infrastructure Solutions
Location: Seattle, WA (On-site / Campus)

About the Role:
GlobalNet is looking for an enthusiastic Network Support Engineer to ensure maximum uptime, security, and performance for our enterprise client networks. You will be responsible for diagnosing network anomalies, supporting switch/router infrastructure, and resolving escalated customer connectivity issues.

Key Responsibilities:
- Monitor and troubleshoot enterprise local area networks (LAN) and wide area networks (WAN).
- Diagnose connectivity, packet loss, and latency issues using Wireshark, ping, traceroute, and packet inspection tools.
- Configure and troubleshoot VLANs (802.1Q), trunk links, and inter-VLAN routing on Layer 2/3 switches.
- Manage IP addressing schemes, subnetting (IPv4/IPv6), DHCP scope allocations, and DNS records.
- Configure and support routing protocols including OSPF and static routes.
- Execute network security standards, including Access Control Lists (ACLs) and port security.
- Document network topologies, incident root causes, and technical troubleshooting guides.
- Automate diagnostic checks using Python or Bash scripts.

Qualifications & Skills:
- Comprehensive understanding of the TCP/IP suite and OSI model.
- Strong practical skills in Subnetting, VLANs, and Routing & Switching.
- Hands-on experience with packet analysis tools like Wireshark.
- Proven network troubleshooting and incident resolution experience.
- Cisco CCNA certification or equivalent networking credential highly desired.
- Scripting knowledge in Python or Bash for network diagnostics is a big plus.
- Associate or Bachelor's degree in Computer Networks, IT, or Computer Science."""
    }
]
