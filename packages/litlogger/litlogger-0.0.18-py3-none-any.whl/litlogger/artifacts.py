# Copyright The Lightning AI team.
# Licensed under the Apache License, Version 2.0 (the "License");
#     http://www.apache.org/licenses/LICENSE-2.0
#
from lightning_utilities import module_available

if module_available("litmodels"):
    # for compatibility with past versions but could be dropped in the future
    from litmodels import download_model, upload_model  # noqa: F401
