# pyQuARC as a service: cloud infrastructure

* Status: approved
* Deciders: @xhagrg
* Date: 2022-05-11

## Context and Problem Statement

pyQuARC is an open source metadata quality assessment tool. Many projects at IMPACT are looking to utilize pyQuARC's assessment for their own metadata. Thus, a need to serve pyQuARC as a service has arisen.

This Architecture Decision Record (ARD) lists the decisions made to create this service.

## Considered Options

1. An EC2 instance running an apache server that hosts a fast api application on top of pyQuARC
2. A Step Function workflow, where one step downloads the metadata and next step runs the validation interfaced with an API gateway
3. An API Gateway interfaced with a Lambda that runs pyQuARC validation

## Decision Drivers

* Scalability
* Low cost

## Decision Outcome

**Chosen option**: An API Gateway interfaced with a Lambda (with pyQuARC on a lambda layer) that runs pyQuARC validation, because

* Since both API Gateway and Lambda follow the "only pay for what you use" pricing framework, it's the cheapest option
* pyQuARC itself has the ability to download the metadata and run the validation. Thus, it doesn't make sense to break into different steps in a Step Function
* Both the API Gateway and Lambda are highly scalable and the scalability is automatically managed by AWS

The **cloud architecture diagram** is linked here:

[QuARC Architecture Diagram](https://lucid.app/lucidchart/60029a21-e153-4d77-a023-33a747c289f4/edit?beaconFlowId=B1515433338621E6&invitationId=inv_88602a11-150a-4800-8176-b1b1d1f38ccb&page=0_0#)

The following resources are to be used:

1. A lambda function to run the actual pyQuARC validation
   * This lambda will use a pyQuARC lambda layer to import pyQuARC
2. An API gateway will act as an interface between the users and the lambda function
   * This will connect to the lambda function using LambdaIntegration
3. A cron job will be scheduled to run once everyday to pull in the latest pyQuARC version and update the lambda layer
   * A manual trigger will also be set up in cases where there's a need to manually update the lambda for critical fixes

All of these are specified in the architecture diagram linked above.
