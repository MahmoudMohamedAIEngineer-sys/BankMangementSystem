# Bank Management System

A desktop banking simulation built with **Python, PySide6, and QML**. The application models the
core of a real banking system — customers, login credentials, accounts, and financial
transactions — with role-based access control, strict lifecycle management, realistic business
rules, and accurate audit trails.

All data lives **in memory** for the duration of the session: the system is an educational
simulation designed to demonstrate sound design and business logic, not a production bank.

---

## Table of Contents

1. [Overview](#1-overview)
2. [Technology Stack](#2-technology-stack)
3. [Project Structure](#3-project-structure)
4. [Getting Started](#4-getting-started)
5. [Architecture](#5-architecture)
6. [Domain Model](#6-domain-model)
7. [Roles & Permissions](#7-roles--permissions)
8. [Authentication](#8-authentication)
9. [Customer Lifecycle](#9-customer-lifecycle)
10. [User & Login Management](#10-user--login-management)
11. [Account Lifecycle](#11-account-lifecycle)
12. [Financial Operations](#12-financial-operations)
13. [Transaction Records & History](#13-transaction-records--history)
14. [Money Handling](#14-money-handling)
15. [Dashboards & Statistics](#15-dashboards--statistics)
16. [Business Rules Summary](#16-business-rules-summary)
17. [Design Decisions & Rationale](#17-design-decisions--rationale)
18. [Suggested Demo Walkthrough](#18-suggested-demo-walkthrough)
19. [Limitations & Possible Extensions](#19-limitations--possible-extensions)

---

## 1. Overview

The system serves two kinds of users:

- **Staff** — bank employees who manage customers, accounts, and logins, and can perform
  financial operations on any account.
- **Customers** — bank clients who log in with personal credentials, see their own accounts,
  and perform deposits, withdrawals, and transfers on accounts they own.

Key characteristics:

| Characteristic | Detail |
|---|---|
| Data storage | Fully in-memory (lists with auto-incrementing IDs); fresh seed on every start |
| Security | argon2 password hashing, ownership checks, permission checks on every service call |
| Money handling | `Decimal` arithmetic, cents-based math, max two decimal places, strict `$#,###.##` formatting |
| Lifecycle management | Customers and users: reversible *active/inactive*; accounts: *active/frozen/closed* with closed as a terminal state |
| Auditability | Every financial operation is recorded as a transaction with source, destination, performer, amount, description, and timestamp |
| History preservation | Records are never deleted; closed accounts keep their numbers reserved and their transaction history visible |

---

## 2. Technology Stack

| Layer | Technology |
|---|---|
| Language | Python 3.9+ |
| GUI framework | PySide6 (Qt 6) with QML declarative UI |
| Password hashing | `argon2-cffi` (`argon2.PasswordHasher`) |
| Money & randomness | Standard library: `decimal`, `secrets`, `datetime` |

---

## 3. Project Structure

```
BankMangementSystem/
├── Main.py                        # Entry point: builds the backend, starts GUI or headless mode
├── requirements.txt               # PySide6, argon2-cffi
│
├── GUI/                           # Presentation layer
│   ├── Main.qml                   # Application window; swaps Login / AppShell
│   ├── Login.qml                  # Sign-in screen with demo-credential hint
│   ├── AppShell.qml               # Sidebar + page loader layout
│   ├── Sidebar.qml                # Role-aware navigation
│   ├── Dashboard.qml              # System dashboard (staff) / personal dashboard (customer)
│   ├── CustomerPage.qml           # Customer records: create, edit, activate/deactivate
│   ├── AccountsPage.qml           # Account records: create, freeze/activate/close
│   ├── TransactionsPage.qml       # Deposit / withdraw / transfer + history & filters
│   ├── UsersPage.qml              # Login management: staff users, customer logins
│   ├── app_controller.py          # AppController: the QObject bridge between QML and services
│   └── components/                # Reusable QML components
│       ├── PrimaryButton.qml
│       ├── SecondaryButton.qml
│       ├── ConfirmDialog.qml
│       ├── StatCard.qml
│       └── StatusBadge.qml
│
├── Models/                        # Domain entities (pure data + entity-level rules)
│   ├── Customer.py                # Customer identity record
│   ├── Users.py                   # User base + StaffUser / CustomerUser (roles & permissions)
│   ├── Account.py                 # Account with balance and the status state machine
│   └── Transaction.py             # Immutable financial record
│
├── Services/                      # Business logic layer
│   ├── Storage.py                 # In-memory repository: collections, IDs, uniqueness, seeding
│   ├── authentication_services.py # Credential hashing/verification, login checks
│   ├── authorization.py           # Permission and ownership enforcement
│   ├── bank_services.py           # Customers, accounts, users, statistics
│   └── Transaction_service.py     # Deposit, withdrawal, transfer, history
│
└── Utils/                         # Cross-cutting helpers
    ├── Constants.py               # Roles, permissions, statuses, types
    ├── Validators.py              # Input validation (name, email, phone, username, password)
    ├── money.py                   # Parsing, cents conversion, formatting
    └── exceptions.py              # BankError hierarchy (Validation, Auth, Permission, NotFound, Duplicate, AccountState, InsufficientFunds)
```

---

## 4. Getting Started

```bash
# 1. Install dependencies
python -m pip install -r requirements.txt

# 2. Run the desktop application
python Main.py

# Optional: quick smoke test without a GUI
python Main.py --headless
```

Headless mode initializes a fresh session, authenticates with the seeded staff account, and
prints the current statistics — useful for verifying that everything boots correctly.

### Demo Accounts

The storage layer seeds one staff account, one customer, and one funded account:

| Account | Username | Password | Notes |
|---|---|---|---|
| Staff | `staff` | `staff123` | Full management capabilities |
| Customer | `customer` | `customer123` | Owns the seeded demo customer |

Seeded data: customer *Demo Customer* (`customer@demo.com`) with savings account
`ACC-DEMO0001` holding **$1,000.00**.

---

## 5. Architecture

The application is a layered design with a strict one-way flow of control. QML never touches
business logic directly; services never touch the UI.

```
┌────────────────────────────────────────────────────────────────┐
│                          GUI  (QML)                            │
│   Login · AppShell · Sidebar · Dashboard · Pages               │
│   (components: buttons, dialogs, stat cards, status badges)    │
└───────────────────────────┬────────────────────────────────────┘
                            │  properties / signals / slots
┌───────────────────────────▼────────────────────────────────────┐
│              AppController  (GUI/app_controller.py)            │
│   loggedIn, role, currentPage, availablePages                  │
│   login / logout / navigate                                    │
│   page data (customers, accounts, transactions, users, stats)  │
│   action slots (create, update, activate, deactivate, ...)     │
│   lastError / lastSuccess messaging                            │
└───────────────────────────┬────────────────────────────────────┘
                            │  service calls — actor always passed along
┌───────────────────────────▼────────────────────────────────────┐
│                         SERVICES                               │
│   AuthenticationService   credential verification             │
│   AuthorizationService    role, permission, ownership checks   │
│   BankService             customers, accounts, users, stats    │
│   TransactionService      deposit, withdraw, transfer, history │
└───────────────────────────┬────────────────────────────────────┘
                            │
┌───────────────────────────▼────────────────────────────────────┐
│                STORAGE  (in-memory repository)                 │
│   users[] · customers[] · accounts[] · transactions[]          │
│   ID generation · uniqueness rules · seed data                 │
└───────────────────────────┬────────────────────────────────────┘
                            │
┌───────────────────────────▼────────────────────────────────────┐
│   MODELS (Customer, User/StaffUser/CustomerUser, Account,      │
│   Transaction)     UTILS (validators, money, constants,        │
│   exceptions) — shared by all layers above                     │
└────────────────────────────────────────────────────────────────┘
```

**Request flow for any action** (e.g. a deposit):

1. The QML page calls a controller slot: `backend.deposit(account, amount, description)`.
2. The controller requires a logged-in user (the *actor*) and invokes the service.
3. The service validates input, checks permissions/ownership via `AuthorizationService`,
   and applies the business rules.
4. On success the storage is updated (balance + transaction record); on failure a
   `BankError` subtype is raised.
5. The controller converts the outcome into `lastSuccess` / `lastError` (shown in the page's
   message banner) and emits `dataChanged`, which makes every open page refresh itself.

**Error handling** is exception-driven with a dedicated hierarchy
(`ValidationError`, `AuthenticationError`, `PermissionDeniedError`, `NotFoundError`,
`DuplicateError`, `AccountStateError`, `InsufficientFundsError`), all deriving from `BankError`.
The controller catches `BankError` and shows its message verbatim; unexpected exceptions are
logged and reported generically.

---

## 6. Domain Model

### Entities

| Entity | Key fields | Responsibility |
|---|---|---|
| `Customer` | `customer_id`, name, phone, email, address, `is_active`, `created_at` | The bank's record of a real-world person (identity only — no credentials) |
| `User` (base) | `user_id`, username, role, `is_active`, password hash | A login identity. `StaffUser` has full staff permissions; `CustomerUser` additionally carries a `customer_id` link |
| `Account` | `account_id`, `account_number`, `customer_id`, type, balance, `status`, `created_at`, `closed_at` | A financial product owned by one customer; owns the balance and status state machine |
| `Transaction` | `transaction_id`, type, amount, source/destination account (id + number snapshot), performer (id + username snapshot), description, `created_at` | An immutable record of one financial operation |

### Relationships

```
                    0..1 login (customer link)
 ┌──────────────┐ ────────────────────────────▶ ┌──────────────────┐
 │   Customer   │                               │       User       │
 │──────────────│                               │──────────────────│
 │ customer_id  │                               │ user_id          │
 │ name         │                               │ username         │
 │ phone        │                               │ role  STAFF /    │
 │ email        │                               │       CUSTOMER   │
 │ address      │                               │ is_active        │
 │ is_active    │                               │ customer_id  ────┼──▶ Customer
 │ created_at   │                               │ password_hash    │
 └──────┬───────┘                               └──────────────────┘
        │ 1..* owns
        ▼
 ┌──────────────┐    appears as source and/or   ┌──────────────────┐
 │   Account    │    destination in             │   Transaction    │
 │──────────────│ ◀──────────────────────────── │──────────────────│
 │ account_id   │                               │ transaction_id   │
 │ account_     │                               │ type  DEPOSIT /  │
 │   number     │                               │  WITHDRAWAL /    │
 │ customer_id  │                               │  TRANSFER        │
 │ type         │                               │ amount           │
 │ balance      │                               │ source /         │
 │ status       │                               │  destination     │
 │ created_at   │                               │ performed_by     │
 │ closed_at    │                               │ description      │
 └──────────────┘                               │ created_at       │
                                                └──────────────────┘
```

Relationship rules:

- A customer has **at most one login** — enforced in storage, so credentials can never be
  duplicated for the same person.
- A staff user is **never linked** to a customer; a customer login **must** be linked to an
  existing customer.
- A customer may own **many accounts**; every account belongs to exactly one customer.
- A transfer transaction connects **two** accounts; a deposit has only a destination; a
  withdrawal has only a source.

---

## 7. Roles & Permissions

Permissions are declared per role in `Models/Users.py` and enforced by
`AuthorizationService` on **every** service call — the UI merely reflects what the backend
already guarantees.

| Capability | Staff | Customer | Enforced permission |
|---|:---:|:---:|---|
| Create / edit / activate / deactivate / search customers | ✔ | ✘ | `MANAGE_CUSTOMERS` |
| Create accounts | ✔ | ✘ | `CREATE_ACCOUNTS` |
| View accounts | all | own only | `VIEW_ALL_ACCOUNTS` / `VIEW_OWN_DATA` |
| Freeze / activate / close accounts | ✔ | ✘ | `MANAGE_ACCOUNT_STATUS` |
| Deposit / withdraw / transfer | any account | own accounts only | `STAFF_FINANCIAL_OPERATIONS` / `CUSTOMER_SELF_SERVICE` |
| View transaction history | all | own only | `VIEW_ALL_TRANSACTIONS` |
| Create staff users and customer logins; activate / deactivate users | ✔ | ✘ | `MANAGE_USERS` |
| View system statistics | ✔ | ✘ | `VIEW_SYSTEM_STATISTICS` |
| Personal dashboard and own data | (system dashboard) | ✔ | `VIEW_OWN_DATA` |

### Page access per role

| Page | Staff sees | Customer sees |
|---|---|---|
| Dashboard | System dashboard (bank-wide statistics) | Personal dashboard (own balance and accounts) |
| Customers | Full customer management | not available |
| Accounts | All accounts + create & status actions | Own accounts, read-only |
| Transactions | All history + operations on any account | Own history + operations on own accounts |
| Users | Login management | not available |

Navigation is guarded in the controller: a customer attempting a staff page (even by calling
`navigate` directly) receives *"You are not authorized to open that page."*

---

## 8. Authentication

Sign-in (`AuthenticationService.authenticate`) performs a strict sequence of checks:

1. **Username format** — lowercased, 3–20 characters, letters/digits/underscore.
2. **Credentials lookup** — the username must exist, and the password must verify against the
   stored argon2 hash.
3. **User status** — a deactivated user cannot sign in.
4. **Linked customer status** — a customer login whose customer profile is inactive cannot
   sign in.

Each failure mode produces a distinct, accurate message — the user is never told "wrong
password" when the real problem is account state:

| Situation | Message shown |
|---|---|
| Unknown username or wrong password | `Username or password is incorrect.` |
| Malformed username input | `Invalid username.` |
| User deactivated by staff | `This user account is inactive.` |
| Linked customer profile deactivated | `The linked customer profile is inactive.` |

Passwords are stored **only** as argon2 hashes; plain passwords are never persisted or logged.

---

## 9. Customer Lifecycle

```
        deactivate
 ┌──────────┐ ──────────▶ ┌────────────┐
 │  ACTIVE  │ ◀────────── │  INACTIVE  │
 └──────────┘  activate   └────────────┘
```

| Operation | Rules |
|---|---|
| Create | Staff only. Name, phone (10–15 digits), email (valid format, lowercased) and address are validated. Email must be unique **among active customers**. |
| Edit | Staff only, same validation. Email uniqueness excludes the customer being edited. |
| Deactivate | Staff only. Sets `is_active = False`. The record is **kept and listed** — nothing is deleted. |
| Activate | Staff only. Restores `is_active = True`. |

**What deactivation does:**

- Blocks the customer's login at authentication time.
- Blocks customer self-service on their accounts.
- Blocks new accounts for the customer (`An inactive customer cannot receive a new account.`).
- Blocks creating a login for the customer (`An inactive customer cannot receive a login.`).

**What deactivation deliberately does not do** (see [Design Decisions](#17-design-decisions--rationale)):

- It does **not** delete or alter the customer's accounts — their statuses are managed
  independently on the Accounts page.
- It does **not** deactivate the login record itself — the user and customer flags are
  separate, and authentication checks both.

The email-uniqueness rule intentionally compares only against *active* customers, so a person
whose previous record was deactivated can be re-registered with the same email.

---

## 10. User & Login Management

All login credentials are managed in **one place**: the Users section. This is a deliberate
single-responsibility rule:

- The **Customers** page manages customer *identity* (who the person is).
- The **Users** page manages *credentials* (how anyone logs in) — for staff and customers alike.

| Operation | Rules |
|---|---|
| Create staff user | Staff only. Username 3–20 chars (letters/digits/underscore, lowercased), password ≥ 6 characters. Created active. |
| Create customer login | Staff only. The linked customer must **exist**, be **active**, and not already have a login. Same username/password rules. |
| Deactivate user | Staff only. Blocks that login immediately. A staff member cannot deactivate their own session (`You cannot deactivate your own active session.`). |
| Activate user | Staff only. Restores the login. |
| List users | Staff only. Shows username, role, linked customer ID, and status. |

Uniqueness guarantees (enforced in storage, not just in the UI):

- Usernames are globally unique, case-insensitively (`Username already exists.`).
- One customer ↔ at most one login (`This customer already has a login.`).
- Staff users can never be linked to a customer profile.

The user list makes the system state transparent at a glance: staff can see exactly which
customers have credentials and whether each login is active.

---

## 11. Account Lifecycle

Accounts have a three-state lifecycle in which **closed is terminal**:

```
                  freeze                    close (balance must be $0.00)
    ┌────────┐ ──────────▶ ┌────────┐ ───────────────────────────▶ ┌─────────┐
    │ ACTIVE │             │ FROZEN │                               │ CLOSED  │
    │        │ ◀────────── │        │                               │ (final) │
    └────────┘  activate   └────────┘                               └─────────┘
         │                                                             ▲
         └────────────────── close (balance must be $0.00) ────────────┘
```

| Status | Meaning | Allowed | Blocked |
|---|---|---|---|
| `ACTIVE` | Fully operational | deposits, withdrawals, transfers (in/out), freezing, closing | — |
| `FROZEN` | Suspended (e.g. review) — funds intact, no movement | re-activation, closing (if balance is zero) | all financial operations (`Account is frozen. Financial operations are not allowed.`) |
| `CLOSED` | Terminated permanently | remains listed and searchable; history stays visible | everything (`Account is closed. Financial operations are not allowed.`) |

**Creation rules**

- Staff only; the owning customer must exist and be **active**.
- Type must be `SAVINGS`, `CURRENT`, or `BUSINESS`.
- The account number is generated by the system (`ACC-` + 10 uppercase hex characters,
  collision-checked) — users never invent numbers, so uniqueness is guaranteed.
- Every account opens at a **$0.00 balance** and is funded by a deposit. This keeps the money
  trail complete: the initial funds are a real, recorded transaction.

**Closing rules**

- An account can only be closed when its balance is **exactly zero**
  (`Account can only be closed when its balance is zero.`) — money never disappears.
- Closing sets `closed_at`, a permanent timestamp.
- A closed account **keeps its number reserved forever** — account numbers are checked against
  all accounts regardless of status, so a number can never be reused or collide.
- A closed account cannot be re-activated or frozen.
- All historical transactions of the account remain visible in the history views.

---

## 12. Financial Operations

All three operations follow the same pipeline:

```
parse & validate amount ─▶ locate account ─▶ authorize actor
        ─▶ validate account state & balance ─▶ apply balance change ─▶ record transaction
```

### Ownership & authorization matrix

| Operation | Staff actor | Customer actor |
|---|---|---|
| Deposit into account X | allowed | only if the customer owns X |
| Withdraw from account X | allowed | only if the customer owns X |
| Transfer from X to Y | allowed | X must be owned by the customer; **Y may be any account** |

Customers can therefore pay other customers (transfer out), but can never move money out of an
account they do not own. Every attempt on a foreign account is rejected with
`You can access only your own accounts.`

### Operation details

| Operation | Validation | Balance effect | Transaction record |
|---|---|---|---|
| **Deposit** | amount > 0, ≤ 2 decimals; account exists and `ACTIVE` | balance += amount | type `DEPOSIT`, destination = account, source = `—` |
| **Withdrawal** | as deposit, plus balance ≥ amount | balance −= amount | type `WITHDRAWAL`, source = account, destination = `—` |
| **Transfer** | source ≠ destination; source passes withdrawal rules; destination passes deposit rules | source −= amount, destination += amount | type `TRANSFER`, both source and destination recorded |

Amount validation is strict and identical everywhere: the value must be a valid finite number
with **at most two decimal places** and **greater than zero** (`Amount must be greater than
zero.`, `Amount cannot contain more than two decimal places.`). Overdrafts are impossible
(`Insufficient funds.`), and a self-transfer is rejected
(`Source and destination accounts must be different.`).

Because a transfer validates both sides **before** moving any money, the two balance changes
are applied together — the operation either completes fully or not at all.

---

## 13. Transaction Records & History

Every financial operation writes **one** immutable transaction containing:

- the **type** (`DEPOSIT` / `WITHDRAWAL` / `TRANSFER`),
- the **amount**,
- the **source** and **destination** accounts — stored both as references and as **text
  snapshots** of the account numbers,
- the **performer** — user reference and a **username snapshot**,
- a free-text **description** (sensible defaults like `"Simulated deposit"` are applied when
  left empty),
- the **timestamp** (UTC, ISO-8601, second precision).

The snapshots make the history self-contained and stable: records always display the account
numbers and username exactly as they were at operation time.

**History views and filters**

| Aspect | Staff | Customer |
|---|---|---|
| Scope | every transaction in the system | only transactions touching the customer's own accounts (including closed ones) |
| Filters | type, account number, date (`YYYY-MM-DD`), free-text search | same filters, always scoped to own accounts |

Filtering by an account the customer does not own is itself rejected as an access violation.
Results are sorted newest first.

---

## 14. Money Handling

All monetary logic runs through `Utils/money.py`:

- Amounts are parsed into `Decimal` — **never** floats — and quantized to whole cents
  (round-half-up).
- More than two decimal places is a validation error.
- Balances are held as `Decimal` and internally converted to integer cents for aggregation,
  so sums are exact.
- Display formatting is uniform: `$1,250.50`.

---

## 15. Dashboards & Statistics

Each statistic corresponds precisely to a labeled database state — no number is approximate
or decorative.

**Staff — system dashboard**

| Card | Meaning |
|---|---|
| Active customers | Customers with `is_active = true` |
| Active accounts | Accounts with status `ACTIVE` (frozen and closed excluded) |
| Total balance | Sum of balances of all non-closed accounts (frozen accounts still hold money, so they are included) |
| Transactions | Total number of recorded transactions |
| Total deposits / withdrawals / transfers | Sum of amounts per transaction type |

The dashboard also lists the eight most recent transactions across the bank.

**Customer — personal dashboard**

| Card | Meaning |
|---|---|
| My accounts | All of the customer's accounts, including closed ones |
| Active accounts | The customer's accounts with status `ACTIVE` |
| My balance | Sum of balances over the customer's non-closed accounts |
| Recent activity | The customer's most recent transactions |

The personal dashboard also lists every account with its type, balance, and status badge.

---

## 16. Business Rules Summary

A compact reference of the invariants the system enforces:

1. One login per customer, ever; staff logins never link to customers.
2. Usernames are globally unique (case-insensitive); emails are unique among active customers.
3. Inactive customers cannot log in, cannot self-serve, and cannot receive new accounts or logins.
4. Accounts are created only for active customers, only by staff, with system-generated
   unique numbers, opening at $0.00.
5. Financial operations require an `ACTIVE` account, a positive amount with ≤ 2 decimals, and
   (for withdrawals and transfers) sufficient balance.
6. Customers may operate only their own accounts; transfer destinations may be any account.
7. Accounts close only at zero balance; closed is terminal, numbers stay reserved, and
   history is preserved.
8. Records (customers, users, accounts, transactions) are never physically deleted — state
   changes are expressed through status flags.
9. Every operation is permission-checked server-side (in the service layer), not just hidden
   in the UI.
10. All money math is exact (`Decimal`/cents); all timestamps are UTC ISO-8601.
11. Record tables (customers, accounts, users) list entries in creation order, so a newly
    added record always appears at the bottom; transaction history is newest-first.

---

## 17. Design Decisions & Rationale

1. **Credentials live only in user management.** Customer identity and login credentials are
   separate concepts, so they are managed in separate places: the Customers page records
   *who the person is*; the Users page controls *how anyone signs in*. This removes any
   ambiguity about who owns the operation, and makes it impossible to end up with a
   half-created customer (identity saved, credentials failed) — each step is an independent,
   fully validated transaction.

2. **Suspension is reversible; closure is terminal.** Customers and users have a symmetric
   activate/deactivate pair because deactivation means *"temporarily barred"* — the record
   stays listed as dormant and may return. Account closure means *"the relationship with this
   product is over"* — it is a one-way door with a timestamp, mirroring real banking where a
   closed account number is never reused. Freezing is the reversible suspension state for
   accounts.

3. **Deactivating a customer does not cascade to their accounts.** Each entity owns its own
   status, and the rules compose: an inactive customer is locked out (login, self-service,
   new accounts, new logins), while the accounts themselves keep their independent statuses.
   Staff retain the ability to service or settle those accounts — e.g. to withdraw remaining
   funds so the account can be closed — which would be impossible if deactivation froze
   everything. In practice, the correct order for ending a relationship is: settle the
   accounts to zero and close them, then deactivate the customer.

4. **Accounts close only at zero balance.** Money must go somewhere before an account
   disappears from active service. This guarantees the transaction ledger and the balances
   always reconcile.

5. **Transactions snapshot their context.** Account numbers and the performer's username are
   copied onto each record, so history reads correctly and consistently even as the live
   entities change state.

6. **Independent status flags, combined at authentication.** A user record and its customer
   profile can be active or inactive independently; authentication checks both and reports
   precisely which one blocked the sign-in. This keeps error messages truthful.

7. **System-generated account numbers.** `ACC-` plus 10 random hex characters
   (`secrets.token_hex`) with a collision check. Users never type account numbers at creation
   time, and closed accounts keep their numbers reserved, so uniqueness is a structural
   guarantee.

8. **Validation and authorization in the service layer, not the UI.** Hiding a button is a UX
   courtesy; the backend re-checks every rule on every call. The UI can therefore never
   create an invalid state, even if it tried.

9. **Deliberately minimal security scope.** The system implements real password hashing,
   RBAC, and ownership checks — and intentionally stops there. Cards, PINs, OTP, KYC, fraud
   detection, and payment gateways are outside the scope of an educational simulation and
   were left out on purpose.

---

## 18. Suggested Demo Walkthrough

A ten-minute script that exercises the whole design:

1. **Login as staff** (`staff` / `staff123`). Point out the system dashboard: active vs.
   total counts, and the seeded $1,000.00 balance.
2. **Customers → Add customer.** Fill in name/phone/email/address. Note that this creates
   *identity only* — no credentials exist yet, by design.
3. **Users → Create customer login.** Link it to the new customer's ID. The users list now
   shows a `CUSTOMER` row with the linked customer ID. Try creating a second login for the
   same customer to show the one-login rule rejecting it.
4. **Accounts → Create account** for the new customer (e.g. `SAVINGS`). The account is
   generated with a unique number and a $0.00 balance.
5. **Transactions:** deposit `500` into the new account, withdraw `120`, and transfer `80`
   from the new account to `ACC-DEMO0001`. Show the history: each row records type, amount,
   source, destination, performer, and timestamp.
6. **Freeze** the new account (Accounts page), then try to deposit into it — the operation is
   rejected with a clear state error. **Activate** it again.
7. **Deactivate** the new customer (Customers page), then try to sign in as the customer
   login created in step 3 — authentication is blocked with
   *The linked customer profile is inactive.* **Activate** the customer again and sign in.
8. **Logout → Login as the customer** (`customer` / `customer123`). Show the personal
   dashboard, the own-accounts view, and the scoped history. Try a deposit into
   `ACC-DEMO0001` (not theirs) to demonstrate the ownership check.
9. **Close an account:** withdraw its balance down to $0.00, then close it. It remains listed
   under the `CLOSED` status filter and its transactions are still in the history.
10. **Try a wrong password** at the login screen to show the accurate messaging, and finish
    with `python Main.py --headless` as a quick boot check.

---

## 19. Limitations & Possible Extensions

**Limitations (by design)**

- Data exists only for the session duration — restarting resets everything to the seed state.
- No password reset mechanism; a forgotten customer password is handled by deactivating the
  login and issuing a new username (one login per customer).
- The Users page references customers by their numeric ID (visible in the customers table)
  rather than a picker.
- Single-user desktop usage; no concurrency or networking.

**Natural extensions** (kept out of scope intentionally)

- Persistent storage (SQLite) behind the existing `Storage` interface.
- A customer-facing profile view.
- Password reset and login renaming.
- Admin/teller role separation if finer-grained permissions are ever needed.
