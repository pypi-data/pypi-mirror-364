# Test MCP Tools

You are going to comprehensively test the Dead Man's Snitch MCP tools in a non-destructive manner. Follow these steps exactly and report the results of each operation.

## Test Plan

1. **List all snitches** - Use the MCP tool to list existing snitches and display a summary
2. **Create a test snitch** - Create a new snitch with specific test parameters
3. **Get snitch details** - Retrieve and display the created snitch's details
4. **Update the snitch** - Modify various attributes of the test snitch
5. **Add tags** - Add multiple tags to the test snitch
6. **Remove a tag** - Remove one of the added tags
7. **Check in** - Send a check-in to the test snitch with a message
8. **Pause the snitch** - Temporarily pause monitoring
9. **Unpause the snitch** - Resume monitoring
10. **Delete the test snitch** - Clean up by removing the test snitch

## Important Instructions

- **ONLY use the MCP tools** - Do NOT use curl, bash commands, or direct API calls
- **Use the exact MCP tool names** starting with `mcp__deadmansnitch__`
- **Report each step's outcome** clearly with success/failure status
- **If any step fails**, continue with the remaining tests and note the failure
- **Use unique identifiers** for the test snitch to avoid conflicts

## Test Execution

### Step 1: List All Snitches
Use `mcp__deadmansnitch__list_snitches` to get the current list of snitches. Display:
- Total count of snitches
- A brief summary of existing snitches (names and statuses)

### Step 2: Create Test Snitch
Use `mcp__deadmansnitch__create_snitch` with these parameters:
- name: "MCP Tool Test Snitch - DELETE ME"
- interval: "hourly"
- notes: "This is a temporary test snitch created to verify MCP tools functionality. Safe to delete."
- alert_type: "basic"

Note: If tags and alert_email parameters cause validation errors, create the snitch without them and add tags in step 5.

Save the token from the response for subsequent operations.

### Step 3: Get Snitch Details
Use `mcp__deadmansnitch__get_snitch` with the token from Step 2 to retrieve full details.

### Step 4: Update Snitch
Use `mcp__deadmansnitch__update_snitch` to modify:
- name: "MCP Tool Test Snitch - UPDATED"
- notes: "Updated notes: This snitch has been modified via MCP tools"
- interval: "daily"

### Step 5: Add Tags
Use `mcp__deadmansnitch__add_tags` to add:
- tags: ["test", "mcp-verification", "temporary"]

### Step 6: Remove Tag
Use `mcp__deadmansnitch__remove_tag` to remove:
- tag: "temporary"

### Step 7: Check In
Use `mcp__deadmansnitch__check_in` with:
- token: (from Step 2)
- message: "Test check-in from MCP tools verification"

### Step 8: Pause Snitch
Use `mcp__deadmansnitch__pause_snitch` with:
- token: (from Step 2)
- until: (calculate an ISO 8601 timestamp 1 hour from now)

### Step 9: Unpause Snitch
Use `mcp__deadmansnitch__unpause_snitch` with the token from Step 2.

### Step 10: Delete Test Snitch
Use `mcp__deadmansnitch__delete_snitch` with the token from Step 2 to clean up.

## Final Report

After completing all steps, provide a summary:
- Which operations succeeded
- Which operations failed (if any)
- Any error messages encountered
- Overall assessment of MCP tools functionality

Remember: This is a comprehensive integration test of the MCP tools. Do not skip steps or use alternative methods. Only use the MCP tools provided.