REPO="nidr0x/homelab"
for ID in $(gh api --method GET "/repos/$REPO/deployments?per_page=100" | jq -r ".[] | .id"); do
    gh api -H "Accept: application/vnd.github+json" -H "X-GitHub-Api-Version: 2022-11-28" --method POST /repos/$REPO/deployments/$ID/statuses -f "state=inactive"
    gh api -H "Accept: application/vnd.github+json" -H "X-GitHub-Api-Version: 2022-11-28" --method DELETE /repos/$REPO/deployments/$ID
done
