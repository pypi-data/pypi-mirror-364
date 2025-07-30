from datetime import datetime
from kg_mem import KGMem
from ontologies.github import github_ontology, developer_type, repository_type, branch_type, commit_type, pull_request_type, issue_type, review_type, release_type
from ontologies.github import owns_type, creates_branch_type, commits_to_type, commit_on_branch_type, opens_pr_type, pr_targets_branch_type, pr_from_branch_type, reviews_pr_type, review_on_pr_type, reports_issue_type, fixes_issue_type, tags_release_type
from ontologies.github import pr_workflow_query_type, developer_activity_query_type, branch_status_query_type, issue_tracking_query_type

# Initialize KGMem with the imported ontology
kg = KGMem(github_ontology)

# Create entities
alice_dev = kg.entity(name="alice", type=developer_type)
bob_dev = kg.entity(name="bob", type=developer_type)
carol_dev = kg.entity(name="carol", type=developer_type)

main_repo = kg.entity(name="awesome-project", type=repository_type)

main_branch = kg.entity(name="main", type=branch_type)
feature_branch = kg.entity(name="feature/new-ui", type=branch_type)
bugfix_branch = kg.entity(name="bugfix/memory-leak", type=branch_type)

commit1 = kg.entity(name="abc123: Initial commit", type=commit_type)
commit2 = kg.entity(name="def456: Add new UI components", type=commit_type)
commit3 = kg.entity(name="ghi789: Fix memory leak in parser", type=commit_type)
commit4 = kg.entity(name="jkl012: Update documentation", type=commit_type)

pr1 = kg.entity(name="PR #42: New UI Implementation", type=pull_request_type)
pr2 = kg.entity(name="PR #43: Critical memory leak fix", type=pull_request_type)

issue1 = kg.entity(name="Issue #10: UI needs redesign", type=issue_type)
issue2 = kg.entity(name="Issue #11: Memory leak in parser", type=issue_type)
issue3 = kg.entity(name="Issue #12: Documentation outdated", type=issue_type)

review1 = kg.entity(name="Review: Looks good with minor changes", type=review_type)
review2 = kg.entity(name="Review: Approved", type=review_type)
review3 = kg.entity(name="Review: Needs changes", type=review_type)

release1 = kg.entity(name="v1.0.0", type=release_type)
release2 = kg.entity(name="v1.1.0", type=release_type)

# Add relations with full sentences
kg += [
    # Repository ownership
    kg.relation(entity0=alice_dev, entity1=main_repo, relation="alice owns awesome-project", type=owns_type),
    
    # Branch creation
    kg.relation(entity0=alice_dev, entity1=feature_branch, relation="alice creates branch feature/new-ui", type=creates_branch_type),
    kg.relation(entity0=bob_dev, entity1=bugfix_branch, relation="bob creates branch bugfix/memory-leak", type=creates_branch_type),
    
    # Commits
    kg.relation(entity0=alice_dev, entity1=commit1, relation="alice authors abc123: Initial commit", type=commits_to_type),
    kg.relation(entity0=alice_dev, entity1=commit2, relation="alice authors def456: Add new UI components", type=commits_to_type),
    kg.relation(entity0=bob_dev, entity1=commit3, relation="bob authors ghi789: Fix memory leak in parser", type=commits_to_type),
    kg.relation(entity0=carol_dev, entity1=commit4, relation="carol authors jkl012: Update documentation", type=commits_to_type),
    
    # Commits on branches
    kg.relation(entity0=commit1, entity1=main_branch, relation="abc123: Initial commit is on branch main", type=commit_on_branch_type),
    kg.relation(entity0=commit2, entity1=feature_branch, relation="def456: Add new UI components is on branch feature/new-ui", type=commit_on_branch_type),
    kg.relation(entity0=commit3, entity1=bugfix_branch, relation="ghi789: Fix memory leak in parser is on branch bugfix/memory-leak", type=commit_on_branch_type),
    kg.relation(entity0=commit4, entity1=main_branch, relation="jkl012: Update documentation is on branch main", type=commit_on_branch_type),
    
    # Pull requests
    kg.relation(entity0=alice_dev, entity1=pr1, relation="alice opens PR #42: New UI Implementation", type=opens_pr_type),
    kg.relation(entity0=bob_dev, entity1=pr2, relation="bob opens PR #43: Critical memory leak fix", type=opens_pr_type),
    
    # PR branches
    kg.relation(entity0=pr1, entity1=main_branch, relation="PR #42: New UI Implementation targets main", type=pr_targets_branch_type),
    kg.relation(entity0=pr1, entity1=feature_branch, relation="PR #42: New UI Implementation originates from branch feature/new-ui", type=pr_from_branch_type),
    kg.relation(entity0=pr2, entity1=main_branch, relation="PR #43: Critical memory leak fix targets main", type=pr_targets_branch_type),
    kg.relation(entity0=pr2, entity1=bugfix_branch, relation="PR #43: Critical memory leak fix originates from branch bugfix/memory-leak", type=pr_from_branch_type),
    
    # Issues
    kg.relation(entity0=carol_dev, entity1=issue1, relation="carol reports Issue #10: UI needs redesign", type=reports_issue_type),
    kg.relation(entity0=carol_dev, entity1=issue2, relation="carol reports Issue #11: Memory leak in parser", type=reports_issue_type),
    kg.relation(entity0=alice_dev, entity1=issue3, relation="alice reports Issue #12: Documentation outdated", type=reports_issue_type),
    
    # PR fixes issues
    kg.relation(entity0=pr1, entity1=issue1, relation="PR #42: New UI Implementation fixes Issue #10: UI needs redesign", type=fixes_issue_type),
    kg.relation(entity0=pr2, entity1=issue2, relation="PR #43: Critical memory leak fix fixes Issue #11: Memory leak in parser", type=fixes_issue_type),
    
    # Reviews
    kg.relation(entity0=bob_dev, entity1=review1, relation="bob writes review Review: Looks good with minor changes", type=reviews_pr_type),
    kg.relation(entity0=carol_dev, entity1=review2, relation="carol writes review Review: Approved", type=reviews_pr_type),
    kg.relation(entity0=alice_dev, entity1=review3, relation="alice writes review Review: Needs changes", type=reviews_pr_type),
    
    # Reviews on PRs
    kg.relation(entity0=review1, entity1=pr1, relation="Review: Looks good with minor changes reviews PR #42: New UI Implementation", type=review_on_pr_type),
    kg.relation(entity0=review2, entity1=pr1, relation="Review: Approved reviews PR #42: New UI Implementation", type=review_on_pr_type),
    kg.relation(entity0=review3, entity1=pr2, relation="Review: Needs changes reviews PR #43: Critical memory leak fix", type=review_on_pr_type),
    
    # Releases
    kg.relation(entity0=commit1, entity1=release1, relation="abc123: Initial commit is tagged as v1.0.0", type=tags_release_type),
    kg.relation(entity0=commit4, entity1=release2, relation="jkl012: Update documentation is tagged as v1.1.0", type=tags_release_type),
]

# Test queries
if __name__ == "__main__":
    # Query 1: PR workflow
    pr_query = kg.query(
        name="What is the status of PR #42?",
        type=pr_workflow_query_type
    )
    
    result = kg.retrieve(pr_query, limit=10)
    
    # Assert retrieval worked
    assert result is not None, "PR query should return a result"
    assert len(result.all_retrievals) > 0, "PR query should retrieve some relations"
    assert any("PR #42" in rel.relation for rel in result.all_retrievals), "Should find PR #42 related activities"
    
    print(f"Query: {pr_query.name}")
    print(f"Result summary: {result.result}")
    print(f"Retrieved relations:")
    for rel in result.all_retrievals:
        print(f"  - {rel.relation}")
    print()
    
    # Query 2: Developer activity
    dev_query = kg.query(
        name="What has alice been working on?",
        type=developer_activity_query_type
    )
    
    result = kg.retrieve(dev_query, limit=8)
    
    # Assert retrieval worked
    assert result is not None, "Developer query should return a result"
    assert len(result.all_retrievals) > 0, "Developer query should retrieve some relations"
    assert any("alice" in rel.relation for rel in result.all_retrievals), "Should find alice's activities"
    
    print(f"Query: {dev_query.name}")
    print(f"Result summary: {result.result}")
    print(f"Retrieved relations:")
    for rel in result.all_retrievals:
        print(f"  - {rel.relation}")
    print()
    
    # Query 3: Issue tracking
    issue_query = kg.query(
        name="Which issues have been fixed?",
        type=issue_tracking_query_type
    )
    
    result = kg.retrieve(issue_query, limit=5)
    
    # Assert retrieval worked
    assert result is not None, "Issue query should return a result"
    assert len(result.all_retrievals) > 0, "Issue query should retrieve some relations"
    assert any("fixes" in rel.relation for rel in result.all_retrievals), "Should find issue fixes"
    
    print(f"Query: {issue_query.name}")
    print(f"Result summary: {result.result}")
    print(f"Retrieved relations:")
    for rel in result.all_retrievals:
        print(f"  - {rel.relation}") 