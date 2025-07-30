
### **3. Integration Strategy**
**Call Python from Bash for heavy tasks:**  
```bash
# Bash calls Python for UUID generation
uuid=$(python3 -c "from uuid import uuid4; print(uuid4())")

# Bash calls Python for structured logging
python3 -c "
from log_utils import log_input
log_input('$(echo "$input" | sed 's/'\''/\\'\''/g')', '$pane_id')
"
```

**Pass state between layers via env vars:**  
```bash
# Bash sets env vars
export PANE_ID="$pane_id"
export CAPTURE="$capture"

# Python reads them
import os
pane_id = os.getenv("PANE_ID")
```

