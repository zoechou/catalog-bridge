@Library('visenze-lib')_

PROJECTS = [
  'gateway',
  'manager',
  'service',
  'worker'
]
def NEED_DEPLOY = false

pipeline {
  // choose a suitable agent to build
  agent {
    label 'build'
  }

  options {
    timestamps()
  }

  stages {
    stage('Checkout') {
      steps {
        // checkout the code from scm (github)
        checkout scm
      }
    }

    stage('Lambda archiving') {
      steps {
        script {
          dir('bridge-lambda') {
            // TODO: Need to remove for release code
            def s3_bucket = 'visenze-lambda-code-bucket-test'
            def aws_cred_id  = 'aws-staging'
            def aws_region = 'us-west-2'

            if(env.BRANCH_NAME in ['production', 'develop']){
              s3_bucket = 'online-sg-enterprise-lambda-code'
              aws_cred_id = 'aws-online-lambda-cd'
              aws_region = 'ap-southeast-1'
            }

            def function_list = sh(script:"ls | grep -v VERSION", returnStdout: true)
            def function_version = sh(script: "cat VERSION | head -1", returnStdout: true)

            for(lambda_function_name in function_list.split('\n')){
              def code_path = "${lambda_function_name}/src"

              try {
                lambda.codeArchive(code_path,
                                lambda_function_name.trim(),
                                function_version.trim(),
                                'Enterprise',
                                'commerce',
                                'commerce',
                                s3_bucket,
                                aws_region,
                                aws_cred_id
                )
                NEED_DEPLOY = true
              }
              catch(all) {
                  print(all)
                  NEED_DEPLOY = false
              }
            }
          }
        }
      }
    }

    stage('Lambda deploy') {
      when {
        expression {
          return NEED_DEPLOY
        }
      }
      steps {
        script {
          // TODO: Need to replace for release code, create workspace first for develop env
          def deploy_workspace = 'test-staging'


          if(env.BRANCH_NAME in ['production']){
            deploy_workspace = 'prod-commerce-connector'
          }
          else if(env.BRANCH_NAME in ['develop']){
            deploy_workspace = 'develop-commerce-connector'
          }

          build(job: 'sre-update-infrastructure', 
                parameters: [string(name: 'INFRASTRUCTURE', value: 'aws-lambda'),
                             string(name: 'INFRA_WORKSPACE', value: "${deploy_workspace}"),
                             string(name: 'CLOUD_FORM_BRANCH', value: "feature/DOS-513"),
                             string(name: 'AGENT_LABEL', value: 'pod-od'),
                             booleanParam(name: 'AUTO_DEPLOY', value: true)])
        }
      }
    }
  }
}

// Get commit sha
def getCommit() {
  return sh(
    script: "(cd '${WORKSPACE}'; git rev-parse HEAD)", returnStdout: true
  ).trim()
}

def getVersion() {
  // read version from pom
  return readMavenPom(file: 'pom.xml').properties.revision
}

// Get snapshot version
def genSnapShotVersion(version) {
  def suffix = "-SNAPSHOT"
    if (!version.endsWith(suffix)) {
      return version + suffix
    }
    return version
}

// Get Release version
def genReleaseVersion(version) {
  def suffix = "-SNAPSHOT"
  if (version.endsWith(suffix)) {
    return version.substring(0, version.length() - suffix.length())
  }
  return version
}

def genDockerTags(branch, commit, version=null, buildNumber=null) {
  def tags = []
  def shortCommit = commit.substring(0, 9)
  tags.add(branch.replaceAll("/", "_"))
  tags.add("${branch.replaceAll("/", "_")}-${shortCommit}")
  //if(branch == 'production') {
  //  assert version !=null
  //  tags.add("${version}")
  //} else {
  //  assert version != null && buildNumber != null
  //  tags.add("${version}.${buildNumber}-${shortCommit}")
  //}
  return tags
}

def isPullRequest(branch) {
  return branch.startsWith('PR')
}

def doLambdacodeTest(branch) {
  return branch == "feature/ES-2397/lambda"
}

def doBuildAndTest(branch) {
  return branch.startsWith('PR') || branch == 'staging' || branch == 'production'
}

def isProdRelease(branch) {
  return env.BRANCH_NAME == "production"
}

def dockerBuild(proj, tag, path) {
  docker.withRegistry(params.DOCKER_REGISTRY, params.DOCKER_REGISTRY_CREDENTIAL) {
    sh "docker build -t visenze/bridge-${proj}:${tag} -f docker/Dockerfile-${proj} ${path}"
  }
}

def dockerPush(proj, localTag, tags) {
  docker.withRegistry(params.DOCKER_REGISTRY, params.DOCKER_REGISTRY_CREDENTIAL) {
    def image = docker.image("visenze/bridge-${proj}:${localTag}")
    tags.each {
      retry(2) {
        image.push(it)
      }
    }
  }
}
