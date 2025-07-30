.. image:: https://img.shields.io/badge/license-AGPL--3-blue.svg
   :target: https://www.gnu.org/licenses/agpl-3.0.html
   :alt: License: AGPL-3

==================
📝 **Description**
==================

**Master Data Mixin** is a core mixin module in the **@simetri-sinergi-id/ssi-mixin** technology suite for Odoo. It provides foundational master data management capabilities that can be mixed into other modules to enable standardized master data handling for various business entities and processes.

It is ideal for Odoo developers who want to ensure their mixin modules are robust, reusable, and easy to maintain.

===================
🔧 **Key Features**
===================

- **Master Data Foundation:** Reusable master data management logic for Odoo modules.
- **Mixin Design:** Built to be inherited by other modules for master data functionality.
- **Deep Integration:** Seamlessly integrates with various business master data types.
- **Open Source:** AGPL-3.0 license with community-driven improvements.

==========================
💡 **Use Cases / Context**
==========================

This mixin is ideal for developers who need to add standardized master data management to their Odoo modules. Common use cases include:

- **Customer Master:** Standardize customer data management across different modules.
- **Supplier Master:** Centralize supplier information and validation logic.
- **Product Master:** Ensure consistent product data structure and validation.
- **Reference Data:** Manage reference tables and lookup values consistently.
- **Custom Modules:** Easily add master data functionality to any custom Odoo module.

Simply inherit from this mixin in your model class and configure the master data pattern according to your business needs.

===================
🚀 **Installation**
===================

To install this module:

1.  Clone the branch **18.0** of the repository: https://github.com/simetri-sinergi-id/ssi-mixin
2.  Add the path to this repository in your Odoo configuration (`addons-path`)
3.  Update the module list (ensure you are in developer mode)
4.  Go to menu *Apps → Apps → Main Apps*
5.  Search for *Master Data Mixin*
6.  Install the module

==========================
� **Installation & Usage**
==========================

1. **Add to Odoo:** Place `ssi_master_data_mixin` in your Odoo addons path.
2. **Enable:** In Odoo Apps, search for `ssi_master_data_mixin` and install.
3. **Extend:** Inherit this mixin in your custom modules to enable master data functionality.

==========
❓ **FAQ**
==========

- **Standalone?** *No, it's a mixin foundation for other modules requiring master data functionality.*
- **Odoo Version?** *Odoo 18 or above.*
- **Contribute?** *Fork, branch, and submit a pull request on* `GitHub <https://github.com/simetri-sinergi-id/ssi-mixin>`_.

==================
🐞 **Bug Tracker**
==================

Bugs are tracked on `GitHub Issues <https://github.com/simetri-sinergi-id/ssi-mixin/issues>`_.
If you encounter any issues, please check if it has already been reported. If not, help us improve by providing detailed feedback.

==============
🙌 **Credits**
==============

This module is developed and maintained by PT. Simetri Sinergi Indonesia. We would like to thank all the contributors who have helped make this module better.

**Contributors:**

- **Core Development:**
  
  - Andhitia Rama <andhitia.r@gmail.com>
  - Asrul Bastian Yunas <asrulbastianyunas@gmail.com>
  - Michael Viriyananda <viriyananda.michael@gmail.com>

- **Community:** Thanks to all community members who reported issues and provided feedback
- **Special Thanks:** To the Odoo Community Association (OCA) for the development guidelines and best practices

===============
**Maintainer:**
===============

.. image:: https://simetri-sinergi.id/logo.png
   :alt: PT. Simetri Sinergi Indonesia
   :target: https://simetri-sinergi.id

This module is maintained by PT. Simetri Sinergi Indonesia.
