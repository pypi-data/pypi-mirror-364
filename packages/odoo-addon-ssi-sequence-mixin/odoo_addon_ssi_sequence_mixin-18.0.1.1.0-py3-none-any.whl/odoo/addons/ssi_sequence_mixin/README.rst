.. image:: https://img.shields.io/badge/license-AGPL--3-blue.svg
   :target: https://www.gnu.org/licenses/agpl-3.0.html
   :alt: License: AGPL-3

==================
📝 **Description**
==================

**Sequence Mixin** is a core mixin module in the **@simetri-sinergi-id/ssi-mixin** technology suite for Odoo. It provides foundational sequence management capabilities that can be mixed into other modules to enable automatic sequence generation for various business documents and processes.

It is ideal for Odoo developers who want to ensure their mixin modules are robust, reusable, and easy to maintain.

===================
🔧 **Key Features**
===================

- **Sequence Mixin Foundation:** Reusable sequence generation logic for Odoo modules.
- **Mixin Design:** Built to be inherited by other modules for sequence functionality.
- **Deep Integration:** Seamlessly integrates with various business document types.
- **Open Source:** AGPL-3.0 license with community-driven improvements.

==========================
💡 **Use Cases / Context**
==========================

This mixin is ideal for developers who need to add automatic sequence generation to their Odoo modules. Common use cases include:

- **Document Numbering:** Automatically generate sequential numbers for invoices, purchase orders, sales orders, etc.
- **Reference Codes:** Create unique reference codes for products, customers, vendors, or internal processes.
- **Workflow Tracking:** Generate sequential IDs for workflow states, approval processes, or task management.
- **Data Management:** Ensure consistent numbering across different business entities and processes.
- **Custom Modules:** Easily add sequence functionality to any custom Odoo module without reinventing the wheel.

Simply inherit from this mixin in your model class and configure the sequence pattern according to your business needs.

===================
🚀 **Installation**
===================

To install this module:

1.  Clone the branch **18.0** of the repository: https://github.com/simetri-sinergi-id/ssi-mixin
2.  Add the path to this repository in your Odoo configuration (`addons-path`)
3.  Update the module list (ensure you are in developer mode)
4.  Go to menu *Apps → Apps → Main Apps*
5.  Search for *Sequence Mixin*
6.  Install the module

==========================
� **Installation & Usage**
==========================

1. **Add to Odoo:** Place `ssi_sequence_mixin` in your Odoo addons path.
2. **Enable:** In Odoo Apps, search for `ssi_sequence_mixin` and install.
3. **Extend:** Inherit this mixin in your custom modules to enable sequence functionality.

==========
❓ **FAQ**
==========

- **Standalone?** *No, it's a mixin foundation for other modules requiring sequence functionality.*
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
