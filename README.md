### Deployment
To trigger deployment, push a new tag to the master branch in the form [0-9].[0-9].[0-9] (such as `1.0.0`).

To create a tag:
`git tag [tag]`

To push:
`git push origin [tag]`

### infx-content-client
Client needs to be able to:
 - Load the most recent active version of a value set, given the name of the value set
 - List of all available versions of a value set, given the name of the value set (as JSON or pandas DataFrame)
 - Load a previous version of a value set, given the ID of that specific version
