# Written Information Security Plan (WISP)
# Kronos Tax Module - IRS Compliance

**Version:** 1.0  
**Effective Date:** 2026-01-26  
**Applicable To:** All tax preparation services using Kronos Tax Module  
**Based On:** IRS Publication 4557, FTC Safeguards Rule, Gramm-Leach-Bliley Act

---

## 1.0 PURPOSE AND SCOPE

### 1.1 Purpose
This Written Information Security Plan (WISP) establishes the framework for protecting client information in compliance with IRS requirements for tax preparers. The plan ensures that sensitive client data is protected against unauthorized access, use, disclosure, modification, or destruction.

### 1.2 Scope
This WISP applies to:
- All client information collected, processed, or stored by the Kronos Tax Module
- All employees, contractors, and third-party service providers with access to client data
- All systems, networks, and physical locations where client data is processed or stored

### 1.3 Definitions
- **Client Information:** Any information relating to an individual client, including but not limited to: name, address, Social Security Number (SSN), Employer Identification Number (EIN), Individual Taxpayer Identification Number (ITIN), financial information, tax returns, and supporting documents.
- **Sensitive Information:** Information that could result in harm to the client if disclosed, including SSN, EIN, ITIN, bank account numbers, and financial data.
- **Covered Data:** All client information subject to this WISP.

---

## 2.0 INFORMATION SECURITY PROGRAM

### 2.1 Information Security Officer
The Information Security Officer (ISO) is responsible for:
- Implementing and maintaining this WISP
- Conducting regular risk assessments
- Training employees on security policies
- Investigating security incidents
- Ensuring compliance with applicable laws and regulations

### 2.2 Risk Assessment
- **Frequency:** Annual assessment, or when significant changes occur
- **Scope:** All systems, processes, and personnel handling client information
- **Methodology:** Identify threats, vulnerabilities, and potential impacts
- **Documentation:** All assessments documented and retained for 3 years

### 2.3 Employee Training
- **Initial Training:** All new employees within 30 days of hire
- **Annual Training:** All employees annually during tax season preparation
- **Content:** Security policies, data handling procedures, incident reporting
- **Documentation:** Training records retained for 3 years

---

## 3.0 DATA CLASSIFICATION AND HANDLING

### 3.1 Data Classification Levels

#### Level 1: Public Information
- Information that may be freely disclosed
- **Examples:** Practice name, contact information, service descriptions

#### Level 2: Internal Information
- Information for internal use only
- **Examples:** Internal procedures, training materials, non-sensitive client communications

#### Level 3: Confidential Information
- Information that could cause harm if disclosed
- **Examples:** Client names, addresses, phone numbers, email addresses

#### Level 4: Sensitive Information
- Information requiring highest level of protection
- **Examples:** SSN, EIN, ITIN, bank account numbers, financial data, tax returns

### 3.2 Handling Requirements

#### Level 1 (Public)
- No special handling required
- May be shared publicly

#### Level 2 (Internal)
- Access limited to employees and contractors
- Must not be disclosed to unauthorized parties

#### Level 3 (Confidential)
- Access limited to employees with need-to-know
- Must be encrypted in transit and at rest
- Must be stored in secure systems

#### Level 4 (Sensitive)
- Access limited to authorized personnel only
- Must be encrypted with AES-256-GCM
- Must have access logging enabled
- Must be retained for minimum 3 years
- Must be securely destroyed after retention period

---

## 4.0 ACCESS CONTROLS

### 4.1 User Authentication
- **Password Requirements:**
  - Minimum 12 characters
  - Must include uppercase, lowercase, numbers, and special characters
  - Must be changed every 90 days
  - Cannot reuse last 5 passwords
- **Multi-Factor Authentication (MFA):** Required for all users accessing client data
- **Session Management:**
  - Automatic logout after 30 minutes of inactivity
  - Maximum session duration: 12 hours
  - Session tokens encrypted and validated

### 4.2 Authorization
- **Role-Based Access Control (RBAC):**
  - Administrator: Full system access
  - Tax Preparer: Client data access, document management
  - Assistant: Limited client data access
  - Client: Own data only
- **Need-to-Know Principle:** Access granted only as necessary for job function
- **Least Privilege:** Users granted minimum permissions required

### 4.3 Access Logging
- **What is logged:**
  - All authentication attempts (successful and failed)
  - All data access (view, edit, delete, download)
  - All file uploads and downloads
  - All export operations
- **Log retention:** 3 years minimum
- **Log review:** Weekly review of access logs by ISO

---

## 5.0 DATA ENCRYPTION

### 5.1 Encryption Standards
- **Algorithm:** AES-256-GCM
- **Key Management:** Hardware Security Module (HSM) or equivalent
- **Key Rotation:** Every 90 days
- **Key Backup:** Encrypted backup in secure location

### 5.2 Data at Rest
- **Database:** All sensitive fields encrypted at column level
- **Files:** All client documents encrypted before storage
- **Backups:** All backups encrypted with separate encryption key

### 5.3 Data in Transit
- **Web Traffic:** TLS 1.3 required for all web communications
- **Email:** Sensitive information only via encrypted email or secure portal
- **API:** All API communications encrypted with TLS 1.3
- **File Transfer:** Secure protocols only (SFTP, HTTPS)

### 5.4 Encryption Exceptions
- No exceptions permitted for sensitive client data
- Temporary exceptions require ISO approval and documented justification

---

## 6.0 DATA RETENTION AND DESTRUCTION

### 6.1 Retention Period
- **Minimum:** 3 years from date of last client interaction
- **IRS Requirement:** 3 years for all tax-related documents
- **State Requirements:** Longer periods may apply based on state law

### 6.2 Retention Categories

#### Category A: Tax Returns and Supporting Documents
- **Retention:** 7 years (3 years minimum, 7 years recommended)
- **Includes:** Tax returns, W-2s, 1099s, receipts, deductions documentation

#### Category B: Client Communications
- **Retention:** 3 years
- **Includes:** Emails, secure messages, notes, correspondence

#### Category C: System Logs
- **Retention:** 3 years
- **Includes:** Access logs, audit trails, security events

#### Category D: Employee Records
- **Retention:** 7 years after termination
- **Includes:** Training records, access authorization records

### 6.3 Secure Destruction
- **Electronic Data:** Secure deletion using DoD 5220.22-M standard
- **Paper Documents:** Cross-cut shredding or professional shredding service
- **Media Destruction:** Physical destruction of storage media
- **Documentation:** Certificate of destruction retained for 3 years

### 6.4 Archival Process
- **Automated Archival:** After retention period, data moved to archival storage
- **Archival Encryption:** Data remains encrypted in archival storage
- **Access Control:** Archived data accessible only to administrators
- **Final Destruction:** After archival period, secure destruction performed

---

## 7.0 PHYSICAL SECURITY

### 7.1 Office Security
- **Access Control:** Keycard or biometric access to office areas
- **Visitor Management:** All visitors logged and escorted
- **After Hours:** Alarm system activated when office unoccupied
- **Secure Areas:** Server rooms and document storage with additional security

### 7.2 Workstation Security
- **Screen Locks:** Automatic after 5 minutes of inactivity
- **Clean Desk Policy:** Sensitive documents not left unattended
- **Secure Storage:** Locking cabinets for paper documents
- **Device Encryption:** All laptops and mobile devices encrypted

### 7.3 Remote Work Security
- **VPN Required:** All remote access via encrypted VPN
- **Home Office:** Basic security requirements for home offices
- **Public Wi-Fi:** Prohibited for accessing client data
- **Device Management:** Company-managed devices only for client data access

---

## 8.0 NETWORK SECURITY

### 8.1 Network Architecture
- **Segmentation:** Separate networks for client data, internal systems, and guest access
- **Firewalls:** Next-generation firewalls with intrusion prevention
- **DMZ:** Public-facing services in demilitarized zone
- **Monitoring:** 24/7 network monitoring and alerting

### 8.2 Wireless Security
- **Encryption:** WPA3 Enterprise required
- **Guest Network:** Separate from internal network
- **Access Control:** MAC address filtering where practical
- **Monitoring:** Regular wireless network scans

### 8.3 Vulnerability Management
- **Scanning:** Weekly vulnerability scans
- **Patching:** Critical patches applied within 7 days
- **Penetration Testing:** Annual external penetration test
- **Remediation:** All vulnerabilities tracked to resolution

---

## 9.0 INCIDENT RESPONSE

### 9.1 Incident Classification

#### Level 1: Minor Incident
- Single client data exposure with low risk
- No financial impact
- **Response Time:** 24 hours

#### Level 2: Moderate Incident
- Multiple clients affected
- Potential financial impact
- **Response Time:** 4 hours

#### Level 3: Major Incident
- Widespread data exposure
- Significant financial or reputational impact
- **Response Time:** 1 hour

#### Level 4: Critical Incident
- Data breach affecting many clients
- Regulatory reporting required
- **Response Time:** Immediate

### 9.2 Incident Response Team
- **Team Lead:** Information Security Officer
- **Members:** IT Director, Legal Counsel, Communications Lead
- **Responsibilities:** Investigation, containment, notification, remediation

### 9.3 Response Procedures
1. **Identification:** Detect and classify incident
2. **Containment:** Isolate affected systems
3. **Investigation:** Determine cause and scope
4. **Eradication:** Remove threat from systems
5. **Recovery:** Restore normal operations
6. **Notification:** Notify affected parties as required by law
7. **Documentation:** Complete incident report
8. **Review:** Lessons learned and process improvement

### 9.4 Notification Requirements
- **Clients:** Notified within 72 hours of discovery if sensitive data exposed
- **Regulators:** As required by state and federal law
- **Credit Bureaus:** If SSNs exposed, notify major credit bureaus
- **Law Enforcement:** If criminal activity suspected

### 9.5 Documentation and Reporting
- **Incident Log:** All incidents logged regardless of severity
- **Incident Reports:** Detailed reports for Level 2+ incidents
- **Retention:** Incident documentation retained for 7 years
- **Annual Report:** Summary of incidents reported to management annually

---

## 10.0 THIRD-PARTY MANAGEMENT

### 10.1 Vendor Assessment
- **Due Diligence:** All vendors assessed before engagement
- **Security Requirements:** Vendors must meet minimum security standards
- **Contractual Requirements:** Security requirements in all contracts
- **Regular Review:** Annual review of vendor security posture

### 10.2 Cloud Service Providers
- **Certifications:** SOC 2 Type II, ISO 27001, or equivalent required
- **Data Location:** Data must remain in United States
- **Access Controls:** Provider must support role-based access
- **Audit Rights:** Right to audit provider security practices

### 10.3 Subcontractors
- **Approval Required:** All subcontractors must be approved
- **Same Standards:** Subcontractors must meet same security standards
- **Liability:** Primary vendor remains liable for subcontractor actions

---

## 11.0 BUSINESS CONTINUITY AND DISASTER RECOVERY

### 11.1 Business Impact Analysis
- **Critical Systems:** Identified and prioritized
- **Recovery Objectives:**
  - Recovery Time Objective (RTO): 4 hours for critical systems
  - Recovery Point Objective (RPO): 1 hour for client data
- **Testing:** Annual testing of recovery procedures

### 11.2 Backup Strategy
- **Frequency:** Daily incremental, weekly full backups
- **Retention:** 30 days on-site, 1 year off-site
- **Encryption:** All backups encrypted
- **Testing:** Monthly restoration testing

### 11.3 Disaster Recovery Sites
- **Hot Site:** Available within 4 hours
- **Data Synchronization:** Real-time or near-real-time
- **Testing:** Semi-annual disaster recovery tests

---

## 12.0 COMPLIANCE AND AUDITING

### 12.1 Regulatory Compliance
- **IRS Requirements:** Publication 4557, Circular 230
- **FTC Safeguards Rule:** 16 CFR Part 314
- **State Laws:** Compliance with all applicable state laws
- **Industry Standards:** NIST Cybersecurity Framework

### 12.2 Internal Audits
- **Frequency:** Quarterly audits of security controls
- **Scope:** Rotating focus on different control areas
- **Reporting:** Findings reported to management
- **Remediation:** All findings tracked to resolution

### 12.3 External Audits
- **Frequency:** Annual external security assessment
- **Scope:** Comprehensive review of security program
- **Reporting:** Formal report with recommendations
- **Action Plan:** Remediation plan for all findings

### 12.4 Documentation Retention
- **Policy Documents:** Retained for 7 years after revision
- **Audit Reports:** Retained for 7 years
- **Training Records:** Retained for 3 years
- **Incident Reports:** Retained for 7 years

---

## 13.0 POLICY MANAGEMENT

### 13.1 Policy Review
- **Annual Review:** This WISP reviewed annually
- **Trigger Events:** Reviewed after significant incidents or changes
- **Approval:** All changes approved by Information Security Officer

### 13.2 Policy Distribution
- **Employees:** All employees receive copy and acknowledge receipt
- **Contractors:** All contractors with data access receive copy
- **Availability:** Current version available to all personnel

### 13.3 Policy Enforcement
- **Violations:** All violations investigated
- **Disciplinary Action:** Up to and including termination
- **Documentation:** All violations and actions documented

### 13.4 Policy Exceptions
- **Approval Required:** All exceptions require ISO approval
- **Documentation:** All exceptions documented with justification
- **Review:** All exceptions reviewed annually

---

## 14.0 ACKNOWLEDGMENT AND TRAINING

### 14.1 Employee Acknowledgment
All employees must sign this acknowledgment:

```
I have read and understand the Written Information Security Plan.
I agree to comply with all policies and procedures contained herein.
I understand that violation of these policies may result in disciplinary
action, up to and including termination of employment.

Employee Name: _________________________
Signature: _____________________________
Date: _________________________________
```

### 14.2 Training Requirements
- **Initial Training:** Within 30 days of hire
- **Annual Training:** During tax season preparation
- **Specialized Training:** Role-specific training as needed
- **Documentation:** All training documented and retained

---

## APPENDIX A: DATA FLOW DIAGRAMS

### A.1 Client Data Flow
```
Client → Secure Portal → Encrypted Storage → Tax Preparer → Secure Delivery → Client
        ↓                    ↓                    ↓
    Encryption           Access Logs         Audit Trail
```

### A.2 Document Retention Flow
```
Active Use (0-1 year) → Annual Archive (1-3 years) → Long-term Archive (3-7 years) → Secure Destruction
```

## APPENDIX B: INCIDENT REPORTING FORM

**Incident Report ID:** [Auto-generated]  
**Date/Time Discovered:** ________________  
**Reported By:** ________________________  
**Incident Type:** [ ] Unauthorized Access [ ] Data Loss [ ] Malware [ ] Other  
**Severity Level:** [ ] 1 [ ] 2 [ ] 3 [ ] 4  
**Systems Affected:** ____________________  
**Clients Affected:** ____________________  
**Initial Description:** _________________  
**Containment Actions:** ________________  
**Notification Required:** [ ] Yes [ ] No  
**Regulatory Reporting:** [ ] Yes [ ] No  

---

## APPENDIX C: RETENTION SCHEDULE

| Data Type | Retention Period | Storage Location | Destruction Method |
|-----------|-----------------|------------------|-------------------|
| Tax Returns | 7 years | Encrypted Database → Archive | Secure Deletion |
| Client Documents | 7 years | Encrypted Storage → Archive | Secure Deletion |
| Client Communications | 3 years | Encrypted Database → Archive | Secure Deletion |
| Access Logs | 3 years | Log Management System | Secure Deletion |
| Backup Tapes | 1 year | Off-site Storage | Physical Destruction |
| Paper Documents | 3 years | Secure Storage | Cross-cut Shredding |

---

*This WISP is automatically enforced by the Kronos Tax Module compliance system. All policies are implemented through technical controls, automated monitoring, and regular audits.*

**Last Reviewed:** 2026-01-26  
**Next Review:** 2027-01-26  
**Information Security Officer:** ________________________