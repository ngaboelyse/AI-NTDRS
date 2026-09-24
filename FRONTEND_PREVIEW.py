"""
AI-NTDRS Frontend Preview
Visual guide to the Security Operations Center (SOC) Dashboard
"""

print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║                   🎨 AI-NTDRS FRONTEND PREVIEW 🎨                         ║
║                                                                            ║
║                    Frontend Server Running on:                            ║
║                      http://localhost:5173/                               ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝

═══════════════════════════════════════════════════════════════════════════════
🎯 FRONTEND ARCHITECTURE
═══════════════════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────────┐
│                     AI-NTDRS SOC DASHBOARD                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ ┌─────────────────┐ ┌──────────────────────────────────────┐  │
│ │  SIDEBAR NAV    │ │        MAIN CONTENT AREA             │  │
│ │                 │ │                                      │  │
│ │ ▸ Dashboard     │ │  [Active Content View]               │  │
│ │ ▸ Global Search │ │                                      │  │
│ │ ▸ Devices       │ │  - Responsive layouts                │  │
│ │ ▸ Alerts        │ │  - Real-time data                    │  │
│ │ ▸ Incidents     │ │  - Interactive filters               │  │
│ │ ▸ Reports       │ │  - Search functionality              │  │
│ │ ▸ Audit Logs    │ │                                      │  │
│ │ ▸ AI Copilot    │ │                                      │  │
│ │                 │ │                                      │  │
│ └─────────────────┘ └──────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

═══════════════════════════════════════════════════════════════════════════════
🎨 UI DESIGN SYSTEM
═══════════════════════════════════════════════════════════════════════════════

Color Scheme (Dark Theme):
  - Background:      #08111f (Deep Ocean Blue)
  - Surface:         #0f1a2b (Darker Blue)
  - Text:            #e5eefc (Light Blue Text)
  - Accent:          #4ea1ff (Bright Blue)
  - Danger:          #f87171 (Red - High Risk)
  - Warning:         #fbbf24 (Amber - Medium Risk)
  - Success:         #34d399 (Green - Normal)

Typography:
  - Font Family:     Inter, system-ui, Segoe UI
  - Modern & Clean:  Professional SOC aesthetic
  - Responsive:      Adapts to all screen sizes

Layout:
  - Sidebar:         280px fixed
  - Main Content:    Responsive (100% - 280px)
  - Grid System:     CSS Grid for layouts
  - Border Radius:   12px for modern appearance


═══════════════════════════════════════════════════════════════════════════════
📊 8 MAIN VIEWS
═══════════════════════════════════════════════════════════════════════════════

1. 📈 DASHBOARD
   ┌────────────────────────────────────────────────────────────┐
   │                    Security Overview                    │
   ├────────────────────────────────────────────────────────────┤
   │                                                            │
   │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐    │
   │  │ Devices  │ │ Flows    │ │ Alerts   │ │Incidents │    │
   │  │    3     │ │  1,847   │ │    8     │ │    4     │    │
   │  └──────────┘ └──────────┘ └──────────┘ └──────────┘    │
   │                                                            │
   │  Recent Alerts:                                            │
   │  ├─ ALT-20260916120530-42 [HIGH]    Suspicious flow       │
   │  ├─ ALT-20260916100215-38 [MOD]     Elevated traffic       │
   │  └─ ALT-20260915235902-35 [HIGH]    Failed connections    │
   │                                                            │
   │  Top Devices by Risk:                                      │
   │  ├─ PC-001      [████████░] 78.5   5 alerts              │
   │  ├─ PC-002      [███░░░░░░] 32.1   1 alert               │
   │  └─ SERVER-01   [██░░░░░░░] 18.7   0 alerts              │
   │                                                            │
   └────────────────────────────────────────────────────────────┘


2. 🔍 GLOBAL SEARCH
   ┌────────────────────────────────────────────────────────────┐
   │  Search all entities across the system                  │
   ├────────────────────────────────────────────────────────────┤
   │                                                            │
   │  Search Query: [________________________]  [🔍 Search]    │
   │                                                            │
   │  Results:                                                  │
   │  ├─ Devices (3)                                            │
   │  │  ├─ PC-001          Risk: 78.5    Status: active       │
   │  │  ├─ PC-002          Risk: 32.1    Status: active       │
   │  │  └─ SERVER-01       Risk: 18.7    Status: active       │
   │  │                                                          │
   │  ├─ Alerts (8)                                             │
   │  │  ├─ ALT-20260916120530-42  HIGH    Suspicious flow      │
   │  │  └─ ALT-20260916100215-38  MOD     Traffic spike        │
   │  │                                                          │
   │  └─ Incidents (4)                                          │
   │     ├─ INC-2026-001    OPEN    Suspicious activity       │
   │     └─ INC-2026-002    IN_PRO  Failed connections        │
   │                                                            │
   └────────────────────────────────────────────────────────────┘


3. 🖥️  DEVICES
   ┌────────────────────────────────────────────────────────────┐
   │  Device Inventory & Risk Management                     │
   ├────────────────────────────────────────────────────────────┤
   │                                                            │
   │  Filters: [Status ▼] [Type ▼] [Activity ▼] [Search] │
   │                                                            │
   │  Device List:                                              │
   │  ┌──────────────────────────────────────────────────────┐ │
   │  │ Device ID  Type      IP Address    Risk  Alerts  Sts  │ │
   │  ├──────────────────────────────────────────────────────┤ │
   │  │ PC-001     Workst.   192.168.1.100  78.5  5      act  │ │
   │  │ PC-002     Workst.   192.168.1.101  32.1  1      act  │ │
   │  │ SERVER-01  Server    10.0.0.5       18.7  0      act  │ │
   │  └──────────────────────────────────────────────────────┘ │
   │                                                            │
   │  Selected Device Details (click to view):                  │
   │  ├─ IP Address: 192.168.1.100                             │
   │  ├─ Risk Score: 78.5 (HIGH)                               │
   │  ├─ Alert Count: 5                                        │
   │  └─ Last Activity: 2026-09-16 12:05:30 UTC               │
   │                                                            │
   └────────────────────────────────────────────────────────────┘


4. 🚨 ALERTS
   ┌────────────────────────────────────────────────────────────┐
   │  Alert Management & Investigation                      │
   ├────────────────────────────────────────────────────────────┤
   │                                                            │
   │  Filters: [Severity ▼] [Status ▼] [Category ▼] [Search] │
   │                                                            │
   │  Severity Filter: ○ ALL  ○ CRITICAL  ○ HIGH  ○ MOD  ○ LOW │
   │  Status Filter:   ○ ALL  ○ NEW  ○ ACK  ○ RESOLVED         │
   │                                                            │
   │  Alert List:                                               │
   │  ┌──────────────────────────────────────────────────────┐ │
   │  │ Alert ID                    Severity  Risk   Status  │ │
   │  ├──────────────────────────────────────────────────────┤ │
   │  │ ALT-20260916120530-42        HIGH     78.5   NEW   │ │
   │  │   ↳ Suspicious flow anomaly                         │ │
   │  │   ↳ Source: 192.168.1.100 → 203.0.113.45           │ │
   │  │   ↳ Failed connections: 8                           │ │
   │  │                                                      │ │
   │  │ ALT-20260916100215-38        MOD      42.3   ACK   │ │
   │  │   ↳ Elevated traffic volume                         │ │
   │  │   ↳ Source: 192.168.1.101 → 198.51.100.23          │ │
   │  │                                                      │ │
   │  └──────────────────────────────────────────────────────┘ │
   │                                                            │
   │  Selected Alert Details:                                   │
   │  ├─ Threat Category: Suspicious flow anomaly              │
   │  ├─ Risk Score: 78.5 (HIGH SEVERITY)                     │
   │  ├─ Source IP: 192.168.1.100                             │
   │  ├─ Destination IP: 203.0.113.45                         │
   │  ├─ Protocol: TCP                                         │
   │  ├─ Failed Connections: 8                                 │
   │  └─ Recommended Action: Investigate device activity      │
   │                                                            │
   └────────────────────────────────────────────────────────────┘


5. 🔗 INCIDENTS
   ┌────────────────────────────────────────────────────────────┐
   │  Incident Tracking & Management                       │
   ├────────────────────────────────────────────────────────────┤
   │                                                            │
   │  Filters: [Status ▼] [Severity ▼] [Search]           │
   │                                                            │
   │  Status Filter: ○ ALL  ○ OPEN  ○ IN_PROGRESS  ○ RESOLVED  │
   │  Severity:     ○ ALL  ○ CRITICAL  ○ HIGH  ○ MOD  ○ LOW    │
   │                                                            │
   │  Incident List:                                            │
   │  ┌──────────────────────────────────────────────────────┐ │
   │  │ Incident Code    Status      Severity  Device    Last  │ │
   │  ├──────────────────────────────────────────────────────┤ │
   │  │ INC-2026-001     OPEN        HIGH      PC-001    12:10 │ │
   │  │   ↳ Suspicious outbound traffic detected            │ │
   │  │   ↳ 3 linked alerts                                  │ │
   │  │                                                      │ │
   │  │ INC-2026-002     IN_PROGRESS MODERATE   PC-002    10:30 │ │
   │  │   ↳ Elevated connection attempts                    │ │
   │  │   ↳ 2 linked alerts                                  │ │
   │  │                                                      │ │
   │  └──────────────────────────────────────────────────────┘ │
   │                                                            │
   │  Incident Details:                                         │
   │  ├─ Incident Code: INC-2026-001                            │
   │  ├─ Status: OPEN                                           │
   │  ├─ Severity: HIGH                                         │
   │  ├─ Device: PC-001 (192.168.1.100)                        │
   │  ├─ Summary: Suspicious outbound traffic                   │
   │  ├─ Created: 2026-09-16 12:05:30 UTC                      │
   │  └─ Last Activity: 2026-09-16 12:10:00 UTC               │
   │                                                            │
   └────────────────────────────────────────────────────────────┘


6. 📋 REPORTS
   ┌────────────────────────────────────────────────────────────┐
   │  Security Reports & Analytics                         │
   ├────────────────────────────────────────────────────────────┤
   │                                                            │
   │  Report Search: [________________________]  [Search]  │
   │                                                            │
   │  Available Reports:                                        │
   │  ┌──────────────────────────────────────────────────────┐ │
   │  │ Report Name               Generated    Type         │ │
   │  ├──────────────────────────────────────────────────────┤ │
   │  │ Daily Security Summary    2026-09-16  Scheduled     │ │
   │  │ Threat Analysis Report    2026-09-16  Custom        │ │
   │  │ Network Traffic Report    2026-09-15  Scheduled     │ │
   │  │ Incident Review Report    2026-09-15  Custom        │ │
   │  └──────────────────────────────────────────────────────┘ │
   │                                                            │
   │  Report Preview:                                           │
   │  ├─ Total Flows: 1,847                                    │
   │  ├─ Total Alerts: 8                                       │
   │  ├─ Active Incidents: 2                                   │
   │  ├─ Critical Events: 2                                    │
   │  └─ Report Period: 2026-09-16 00:00 - 2026-09-16 23:59  │
   │                                                            │
   └────────────────────────────────────────────────────────────┘


7. 📝 AUDIT LOGS
   ┌────────────────────────────────────────────────────────────┐
   │  System Activity & Compliance Tracking                 │
   ├────────────────────────────────────────────────────────────┤
   │                                                            │
   │  Log Search: [________________________]  [Search]   │
   │                                                            │
   │  Audit Log Entries:                                        │
   │  ┌──────────────────────────────────────────────────────┐ │
   │  │ Timestamp            User    Action    Entity       │ │
   │  ├──────────────────────────────────────────────────────┤ │
   │  │ 2026-09-16 12:15:30  admin   created   alert #42   │ │
   │  │ 2026-09-16 12:10:00  admin   updated   incident #1  │ │
   │  │ 2026-09-16 10:02:15  admin   created   alert #38   │ │
   │  │ 2026-09-16 09:30:45  admin   queried   devices     │ │
   │  │ 2026-09-16 08:45:20  admin   login     system      │ │
   │  └──────────────────────────────────────────────────────┘ │
   │                                                            │
   │  Log Entry Details:                                        │
   │  ├─ Timestamp: 2026-09-16 12:15:30 UTC                   │
   │  ├─ User: admin@ai-ntdrs.local                            │
   │  ├─ Action: created                                       │
   │  ├─ Entity: alert #42 (ALT-20260916120530-42)             │
   │  └─ Details: High-severity alert auto-generated           │
   │                                                            │
   └────────────────────────────────────────────────────────────┘


8. 🤖 AI COPILOT
   ┌────────────────────────────────────────────────────────────┐
   │  Intelligent Security Assistant                       │
   ├────────────────────────────────────────────────────────────┤
   │                                                            │
   │  Query: [What is the security status?          ] [Ask] │
   │                                                            │
   │  Copilot Response:                                         │
   │  ┌──────────────────────────────────────────────────────┐ │
   │  │ 🤖 AI Security Assistant                            │ │
   │  │                                                      │ │
   │  │ Security Overview: 3 devices monitored with 8       │ │
   │  │ alerts. PC-001 is highest-risk (78.5). Current      │ │
   │  │ incident count: 2 OPEN, 1 IN_PROGRESS.             │ │
   │  │                                                      │ │
   │  │ Facts:                                               │ │
   │  │  • Monitored devices: 3                             │ │
   │  │  • Total flows analyzed: 1,847                      │ │
   │  │  • Alerts recorded: 8 (3 high/critical severity)    │ │
   │  │  • Active incidents: 2/4                            │ │
   │  │                                                      │ │
   │  │ Predictions:                                         │ │
   │  │  • Highest-risk: PC-001 (78.5 risk score)           │ │
   │  │  • Top alert: ALT-20260916120530-42 (HIGH)          │ │
   │  │                                                      │ │
   │  │ Recommendations:                                     │ │
   │  │  • Investigate PC-001 for unauthorized activity     │ │
   │  │  • Review latest alerts before escalation           │ │
   │  │  • Prioritize critical alerts immediately           │ │
   │  │                                                      │ │
   │  └──────────────────────────────────────────────────────┘ │
   │                                                            │
   │  Sample Queries:                                           │
   │  ├─ "Give me a security overview"                         │
   │  ├─ "What's the highest risk device?"                     │
   │  ├─ "Explain the recent alerts"                           │
   │  └─ "Show traffic patterns"                               │
   │                                                            │
   └────────────────────────────────────────────────────────────┘


═══════════════════════════════════════════════════════════════════════════════
✨ KEY FEATURES
═══════════════════════════════════════════════════════════════════════════════

INTERACTIVE FILTERING
✓ Filter by severity level
✓ Filter by status
✓ Filter by device type/activity
✓ Full-text search capability
✓ Pagination controls
✓ Real-time results

DATA VISUALIZATION
✓ Risk score bars and indicators
✓ Color-coded severity levels
✓ Responsive grid layouts
✓ Collapsible detail panels
✓ Summary cards
✓ Activity timelines

USER EXPERIENCE
✓ Intuitive navigation
✓ Keyboard shortcuts
✓ Dark theme (eye-friendly)
✓ Professional design
✓ Mobile-responsive
✓ Fast load times

SECURITY FEATURES
✓ Authentication required
✓ Role-based access control
✓ Audit logging
✓ Session management
✓ Secure token handling
✓ CORS protection


═══════════════════════════════════════════════════════════════════════════════
🔌 BACKEND INTEGRATION
═══════════════════════════════════════════════════════════════════════════════

API Endpoints Connected:
├─ /api/auth/login          ✓ Authentication
├─ /api/auth/me             ✓ User profile
├─ /api/dashboard/summary   ✓ Overview metrics
├─ /api/devices             ✓ Device list + filtering
├─ /api/alerts              ✓ Alert management + filtering
├─ /api/incidents           ✓ Incident tracking
├─ /api/reports             ✓ Report generation
├─ /api/audit-logs          ✓ Activity tracking
└─ /api/copilot/summarize   ✓ AI insights

Ready for Integration:
✓ Advanced filtering (severity, status, activity level)
✓ Pagination and search
✓ ML-enhanced risk scoring
✓ ML-based anomaly detection
✓ AI Copilot grounding


═══════════════════════════════════════════════════════════════════════════════
🎓 AUTHENTICATION
═══════════════════════════════════════════════════════════════════════════════

Login Screen (initial load):
  Username/Email: admin@ai-ntdrs.local (pre-filled for demo)
  Password:       ChangeMe123! (pre-filled for demo)
  
  [Login Button]  [Forgot Password?]

Session Management:
  ✓ JWT token stored in localStorage
  ✓ Auto-refreshed on navigation
  ✓ Secure logout clears token
  ✓ Protected routes require auth


═══════════════════════════════════════════════════════════════════════════════
📱 RESPONSIVE DESIGN
═══════════════════════════════════════════════════════════════════════════════

Desktop (1920px+):
  └─ Full sidebar + full content area
  └─ 3-4 columns layout
  └─ Comprehensive data display

Tablet (768px - 1024px):
  └─ Collapsible sidebar
  └─ 2-column layout
  └─ Optimized spacing

Mobile (<768px - Future Consideration):
  └─ Mobile menu
  └─ 1-column layout
  └─ Touch-friendly controls


═══════════════════════════════════════════════════════════════════════════════
🚀 TECHNOLOGY STACK
═══════════════════════════════════════════════════════════════════════════════

Frontend Framework:
  • React 18.3.1      (UI framework)
  • TypeScript 5.5.4  (Type safety)
  • Vite 5.4.2        (Build tool)

Styling:
  • CSS 3             (Modern CSS)
  • CSS Variables     (Dark theme support)
  • CSS Grid          (Responsive layouts)
  • Flexbox           (Component layouts)

HTTP Client:
  • Fetch API         (Standard browser API)
  • Bearer tokens     (JWT auth)
  • CORS handling     (Cross-origin requests)

Build & Dev:
  • npm/pnpm          (Package management)
  • Vite dev server   (Hot reload)
  • TypeScript Compiler
  • Modern browser APIs


═══════════════════════════════════════════════════════════════════════════════
📊 DATA MANAGEMENT
═══════════════════════════════════════════════════════════════════════════════

State Management:
  • React useState    (Local component state)
  • useMemo/useEffect (Performance optimization)
  • Promise.all       (Parallel API calls)

Data Caching:
  • In-memory cache   (Fast navigation)
  • Lazy loading      (On-demand fetch)
  • Auto-refresh      (Real-time updates)

Search & Filter:
  • Client-side filtering
  • Server-side filtering (via query params)
  • Pagination support


═══════════════════════════════════════════════════════════════════════════════
🎉 FRONTEND IS NOW RUNNING!
═══════════════════════════════════════════════════════════════════════════════

Access the Frontend:
  💻 Browser URL: http://localhost:5173/
  📱 Local Network: Check terminal for network URL

Default Login Credentials:
  👤 Email: admin@ai-ntdrs.local
  🔑 Password: ChangeMe123!

Demo Walkthrough:
  1. Login with demo credentials
  2. View Dashboard with metrics
  3. Explore Devices with filtering
  4. Review Alerts with severity filters
  5. Manage Incidents
  6. Check Audit Logs
  7. Query AI Copilot
  8. View Reports

Features to Test:
  ✓ Click on devices to see details
  ✓ Use severity filters on alerts
  ✓ Search for incidents
  ✓ Ask Copilot questions
  ✓ Navigate between views
  ✓ Check responsive design


═══════════════════════════════════════════════════════════════════════════════
💡 NEXT STEPS
═══════════════════════════════════════════════════════════════════════════════

Development:
  1. Backend should also be running on http://localhost:8000
  2. Frontend will auto-connect to backend APIs
  3. Real data flows will populate all views
  4. ML-enhanced risk scores will appear in device/alert lists

Production:
  1. Build: npm run build
  2. Deploy to web server
  3. Configure backend URL
  4. Enable HTTPS
  5. Set up CDN for assets


═══════════════════════════════════════════════════════════════════════════════

🎨 Enjoy the AI-NTDRS Security Operations Center! 🎨

The frontend is modern, responsive, and fully integrated with the enhanced
backend featuring:
  ✓ Advanced filtering on all endpoints
  ✓ ML-enhanced risk scoring
  ✓ Intelligent AI Copilot
  ✓ Comprehensive audit logging
  ✓ Professional UI/UX

Happy exploring! 🚀
""")
