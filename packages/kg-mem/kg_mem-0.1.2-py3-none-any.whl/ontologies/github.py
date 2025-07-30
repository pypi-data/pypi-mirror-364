"""
GitHub objects ontology for software development workflows.
"""

from datetime import datetime
from kg_mem import Ontology, EntityType, RelationType, QueryType


# Entity types
developer_type = EntityType(name="Developer", created_at=datetime.now())
repository_type = EntityType(name="Repository", created_at=datetime.now())
branch_type = EntityType(name="Branch", created_at=datetime.now())
commit_type = EntityType(name="Commit", created_at=datetime.now())
pull_request_type = EntityType(name="PullRequest", created_at=datetime.now())
issue_type = EntityType(name="Issue", created_at=datetime.now())
review_type = EntityType(name="Review", created_at=datetime.now())
release_type = EntityType(name="Release", created_at=datetime.now())

# Relation types
owns_type = RelationType(
    entity_type0=developer_type,
    entity_type1=repository_type,
    name="owns",
    context="Developer owns a repository",
    created_at=datetime.now()
)

creates_branch_type = RelationType(
    entity_type0=developer_type,
    entity_type1=branch_type,
    name="creates_branch",
    context="Developer creates a new branch",
    created_at=datetime.now()
)

commits_to_type = RelationType(
    entity_type0=developer_type,
    entity_type1=commit_type,
    name="authors",
    context="Developer authors a commit",
    created_at=datetime.now()
)

commit_on_branch_type = RelationType(
    entity_type0=commit_type,
    entity_type1=branch_type,
    name="on_branch",
    context="Commit exists on a branch",
    created_at=datetime.now()
)

opens_pr_type = RelationType(
    entity_type0=developer_type,
    entity_type1=pull_request_type,
    name="opens",
    context="Developer opens a pull request",
    created_at=datetime.now()
)

pr_targets_branch_type = RelationType(
    entity_type0=pull_request_type,
    entity_type1=branch_type,
    name="targets",
    context="Pull request targets a branch for merging",
    created_at=datetime.now()
)

pr_from_branch_type = RelationType(
    entity_type0=pull_request_type,
    entity_type1=branch_type,
    name="from_branch",
    context="Pull request originates from a branch",
    created_at=datetime.now()
)

reviews_pr_type = RelationType(
    entity_type0=developer_type,
    entity_type1=review_type,
    name="writes_review",
    context="Developer reviews a pull request",
    created_at=datetime.now()
)

review_on_pr_type = RelationType(
    entity_type0=review_type,
    entity_type1=pull_request_type,
    name="reviews",
    context="Review is for a specific pull request",
    created_at=datetime.now()
)

reports_issue_type = RelationType(
    entity_type0=developer_type,
    entity_type1=issue_type,
    name="reports",
    context="Developer reports an issue",
    created_at=datetime.now()
)

fixes_issue_type = RelationType(
    entity_type0=pull_request_type,
    entity_type1=issue_type,
    name="fixes",
    context="Pull request fixes an issue",
    created_at=datetime.now()
)

tags_release_type = RelationType(
    entity_type0=commit_type,
    entity_type1=release_type,
    name="tagged_as",
    context="Commit is tagged as a release",
    created_at=datetime.now()
)

# Query types
pr_workflow_query_type = QueryType(
    name="Pull request workflow query",
    context="Understanding the lifecycle of pull requests",
    types_to_retrieve=[pull_request_type, opens_pr_type, reviews_pr_type, pr_targets_branch_type, fixes_issue_type]
)

developer_activity_query_type = QueryType(
    name="Developer activity query",
    context="Tracking developer contributions",
    types_to_retrieve=[developer_type, commits_to_type, opens_pr_type, reports_issue_type, reviews_pr_type]
)

branch_status_query_type = QueryType(
    name="Branch status query",
    context="Understanding branch activity and merges",
    types_to_retrieve=[branch_type, commit_on_branch_type, pr_targets_branch_type, pr_from_branch_type]
)

issue_tracking_query_type = QueryType(
    name="Issue tracking query",
    context="Tracking issues and their resolutions",
    types_to_retrieve=[issue_type, reports_issue_type, fixes_issue_type]
)

# GitHub ontology object
github_ontology = Ontology(
    entity_types=[developer_type, repository_type, branch_type, commit_type, pull_request_type, 
                  issue_type, review_type, release_type],
    relation_types=[owns_type, creates_branch_type, commits_to_type, commit_on_branch_type, opens_pr_type, 
                   pr_targets_branch_type, pr_from_branch_type, reviews_pr_type, review_on_pr_type, 
                   reports_issue_type, fixes_issue_type, tags_release_type],
    query_types=[pr_workflow_query_type, developer_activity_query_type, branch_status_query_type, issue_tracking_query_type]
) 