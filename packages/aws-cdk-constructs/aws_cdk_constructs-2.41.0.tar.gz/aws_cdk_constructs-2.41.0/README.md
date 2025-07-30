

# Start here
FAO AWS CDK is library to build FAO-compliant AWS infrastructure in near-zero time-to-market.

CSI Cloud Team developed a set of highly reusable AWS infrastructural building-blocks in collaboration with the Unix Admin Team and Statistical Working System (SWS) development team.

To adopt FAO AWS CDK enhances the projects' robustness over the time as they will inherit the benefits of a centralized infrastructural development, they can keep the focus on application features development.

These shared infrastructural building-blocks natively implement FAO AWS best practices and abstract low-level technical details, while enabling AWS developers to focus on code production.

As a major positive side effect, the overal sustainability of the FAO AWS cloud environment reaches the stars 🚀.

- [Python package index of FAO AWS CDK](https://pypi.org/project/aws-cdk-constructs/)
- [Source on Bitbucket of FAO AWS CDK](https://bitbucket.org/cioapps/aws-cdk-constructs)

## Prerequisites
Make sure your local machine is configured to meet the [FAO AWS prerequisites](https://aws.fao.org/docs/cdk/introduction/#prerequisites)
and you have a general undestanding of what AWS CDK is and how to use it. 

- [AWS CDK introuction](https://aws.amazon.com/cdk/)
- [AWS CDK - YouTube video](https://www.youtube.com/watch?time_continue=1&v=bz4jTx4v-l8)
- [AWS CDK Workshop - Python](https://cdkworkshop.com/30-python.html)

## Documentation, reference architectures, tutorials, and more

CSI Cloud Team produced extensive documentation about FAO AWS CDK (and FAO AWS in general).
- [FAO CDK intro](https://aws.fao.org/docs/cdk/introduction/).
- [FAO CDK project structure](https://aws.fao.org/docs/cdk/project_structure/).
- [FAO CDK reference architectures, ready to be copied](https://aws.fao.org/docs/cdk/reference_architectures/).
- [Common issues and troubleshooting with FAO CDK](https://aws.fao.org/docs/cdk/troubleshooting/).
- [Video tutorials](https://aws.fao.org/docs/tutorials/video_tutorials/).

## Getting started

### Local project initialization

 - If you project is officially started, you can request a new Bitbucket.org repo for you cloud infrastructure
 - CSI Cloud Team created a [skeleon project](https://bitbucket.org/cioapps/aws-cdk-template-iac) to simplify the onboarding to FAO CDK and what the repository will contains will be identical to [this](https://bitbucket.org/cioapps/aws-cdk-template-iac). The repository will be already configured to implement CD/CI;
 - Browser the `app.py` file to examples of how to intantiate FAO CDK resources with relative explainations
 - Follow the [FAO Development lifecycle](https://aws.fao.org/docs/csi_managed/development_lifecycle/) to release your cloud solution in the development environment;
 - [Your path towards production](https://aws.fao.org/docs/csi_managed/your_path_towards_production/) describes how to release your solution in the production environment;
 - [The FAO AWS automation](https://aws.fao.org/docs/csi_managed/automation/) website describes in depth how the automation is implemented in the FAO AWS environment.

### Useful commands

`<ENV>` possible values: `development`, `qa`, `production`.

Kindly note, that the correspondent `.env.<ENV>-iac` file must exist to run a given command. For more information please refer to [How to configure your FAO CDK stack](https://aws.fao.org/docs/cdk/cd_ci/#how-to-configure-your-fao-cdk-stack)

 - `ENVIRONMENT=<ENV> cdk ls`          list all stacks in the app
 - `ENVIRONMENT=<ENV> cdk synth`       emits the synthesized CloudFormation template
 - `ENVIRONMENT=<ENV> cdk deploy`      deploy this stack to your default AWS account/region
 - `ENVIRONMENT=<ENV> cdk diff`        compare deployed stack with current state
 - `ENVIRONMENT=<ENV> cdk docs`        open CDK documentation
 - `ENVIRONMENT=<ENV> cdk ls`: to list the available stacks in the projects
 - `ENVIRONMENT=<ENV> cdk synth MY_STACK --profile my-dev`: to synthetize (generate) the cloud formation template of MY_STACK stack
 - `ENVIRONMENT=<ENV> cdk deploy MY_STACK --profile my-dev`: to deploy the MY_STACK stack


### How to generate the AWS CDK constructs documentation
The documentation follows Google format.

 * Browse the `./docs` directory
 * Run the `make html` to generate the static HTML documentation in the  `/docs/_build/` directory

The documentation release is scripted in the pipeline. So you will simply need to release your code in the `master` branch of the repository to see the FAO CDK documentation published. 

### How to release a new version of AWS CDK constructs

The release of the constructs in `pypi` is automated in the CD/CI pipeline. So you will simply need to release your code in the `master` branch of the repository to see the FAO CDK documentation published and your constructs available on `pypi`. 
Before to move your code in the `master` branch, remember to upgrade the version of the constructs as following:
- Commit your changes, each commit in the repository should follow the convention: [https://www.conventionalcommits.org/en/v1.0.0/](https://www.conventionalcommits.org/en/v1.0.0/)
- Run `npm run release` to auto generate the `CHANGELOG.md` file and upgrade the constructs version.
- Pull request the code to the master branch of the repo

If you try to release a version already published (i.e. you forget to upgrade the package version in the mentioned file) the release will fail. 
Check out the CD/CI pipeline for additional information.

### How can I test my new FAO CDK version before to publish it?

- Open the `IAC` project you are working on, and create a `git` branch for the feature you are developing
- Install the project dependencies using `pip install -r requirements.txt`
- Locally install the `FAO CDK` constructs using `pip install -e ../../cdk/aws-cdk-constructs/` (NB: the path in your file system may vary). This implies that you cloned the `FAO CDK` repository on your local machine, and the repository is configured to use the `develop` branch
- Modify in the local `FAO CDK` repo the code to implement the desired infrastructural resources
- You can test the `FAO CDK` deployment from the `IAC` repository, using the `CDK CLI` (e.g. `cdk deploy YOUR_STACK --profile YOUR_PROFILE`). This will read from your local `FAO CDK` repository the new modifications you just developed to include them in the deployement
- Once the `FAO CDK` development is completed, release the new `FAO CDK` version as described above and update the `requirements.txt` files in the `IAC` repository
- Once the `IAC` repository is pushed on Bitbucket, it'll download the newly release `FAO CDK` version during the CD/CI pipeline execution.

### How can I automatically lint my code before each commit

There is a check on the pipeline to ensure the code and tests pass the blue linting, to ensure the code is properly formatted you can add the (pre-commit)[./.pre-commit-config.yaml] hook to your local repository.
```
pip install -r requirements-dev.txt
pre-commit install
```
This will run the linter and lint all the files under aws_cdk_constructs and tests before each commit. If you see that some files failed the tests, blue will automatically fix them for you. You will only have to stage those files back and commit again.