import streamlit as st
import requests

st.set_page_config(page_title="GitHub Model Runner", page_icon="🤖", layout="centered")

st.title("🤖 GitHub Model Runner")
st.markdown("Download and run a Hugging Face text-generation model on **GitHub Actions**.")

# --- Sidebar Configuration ---
st.sidebar.header("GitHub Settings")
github_token = st.sidebar.text_input(
    "GitHub PAT (Personal Access Token)",
    type="password",
    help="Requires Actions: write permission (fine-grained token) or the appropriate classic token scopes.",
)
repo_owner = st.sidebar.text_input("Repository Owner / Username", value="jaloo0")
repo_name = st.sidebar.text_input("Repository Name", value="AirLLM")
workflow_file = st.sidebar.text_input("Workflow Filename", value="airllm.yml")

# --- Main Dashboard Area ---
st.markdown("### Model Prompt")
model_id = st.text_input(
    "Hugging Face model ID",
    value="HuggingFaceTB/SmolLM2-360M-Instruct",
    help="The model is downloaded to the temporary GitHub Actions runner. Larger models may exceed its memory or time limits.",
)
prompt_text = st.text_area(
    "Enter the prompt you want to send to the model:",
    value="Explain how layer-wise GPU inference works in 2 sentences.",
    height=100
)

if st.button("🚀 Trigger Workflow Dispatch", type="primary"):
    if not github_token:
        st.error("Please provide your GitHub Personal Access Token in the sidebar.")
    elif not repo_owner or not repo_name:
        st.error("Please provide both the repository owner and repository name.")
    elif not model_id.strip():
        st.error("Please provide a Hugging Face model ID.")
    else:
        # GitHub REST API endpoint for workflow dispatch
        url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/actions/workflows/{workflow_file}/dispatches"
        
        headers = {
            "Authorization": f"Bearer {github_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        
        payload = {
            "ref": "main",
            "inputs": {"prompt": prompt_text, "model_id": model_id}
        }
        
        with st.spinner("Sending dispatch request to GitHub API..."):
            try:
                response = requests.post(url, headers=headers, json=payload, timeout=30)
                
                # GitHub returns a 204 No Content status on successful dispatch
                if response.status_code == 204:
                    st.success("Workflow successfully triggered! 🎉")
                    actions_url = f"https://github.com/{repo_owner}/{repo_name}/actions"
                    st.info(f"Because GitHub Actions runs asynchronously, check the live logs and output here:\n\n👉 [{actions_url}]({actions_url})")
                else:
                    st.error(f"Failed to trigger workflow. Response Status: {response.status_code}")
                    st.json(response.json() if response.text else {"error": "Empty response body"})
            except Exception as e:
                st.error(f"An error occurred while connecting to the GitHub API: {e}")
