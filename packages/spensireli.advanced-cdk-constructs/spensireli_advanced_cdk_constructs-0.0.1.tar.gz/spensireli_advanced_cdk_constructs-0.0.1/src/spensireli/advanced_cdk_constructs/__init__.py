r'''
# Advanced CDK Constructs

A collection of advanced AWS CDK constructs to simplify AWS.

## Installation

### From NPM

```bash
npm install advanced-cdk-constructs
```

### From GitHub

```bash
npm install git+https://github.com/spensireli/advanced-cdk-constructs.git
```

## Available Constructs

### GuardDuty Construct

The `GuardDutyConstruct` provides a simplified way to deploy AWS GuardDuty with common security configurations.

#### Import

```python
import { GuardDutyConstruct, GuardDutyConstructProps } from 'advanced-cdk-constructs';
```

#### Basic Usage

```python
import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { GuardDutyConstruct } from 'advanced-cdk-constructs';

export class MyStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // Create GuardDuty with default settings
    const guardDuty = new GuardDutyConstruct(this, 'MyGuardDuty');
  }
}
```

#### Advanced Configuration

```python
import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { GuardDutyConstruct, GuardDutyConstructProps } from 'advanced-cdk-constructs';

export class MyStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const guardDutyProps: GuardDutyConstructProps = {
      enableGuardDuty: true,
      kubernetesAuditLogs: true,
      malwareProtection: true,
      s3Logs: true,
    };

    const guardDuty = new GuardDutyConstruct(this, 'MyGuardDuty', guardDutyProps);

    // Access the detector ID for other resources
    console.log('GuardDuty Detector ID:', guardDuty.detectorId);
  }
}
```

#### Configuration Options

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `enableGuardDuty` | `boolean` | `true` | Whether to enable GuardDuty |
| `kubernetesAuditLogs` | `boolean` | `true` | Enable Kubernetes audit logs monitoring |
| `malwareProtection` | `boolean` | `true` | Enable malware protection for EC2 instances |
| `s3Logs` | `boolean` | `true` | Enable S3 logs monitoring |

#### Features

* **Runtime Monitoring**: Automatically enabled for comprehensive threat detection
* **Kubernetes Audit Logs**: Monitors Kubernetes cluster activities
* **Malware Protection**: Scans EC2 instances for malware
* **S3 Logs Monitoring**: Monitors S3 bucket activities for suspicious behavior
* **Detector ID Access**: Public property to reference the detector in other constructs

## Development

### Prerequisites

* Node.js 22.0.0 or higher
* AWS CDK CLI
* TypeScript

### Setup

1. Clone the repository:

```bash
git clone git@github.com:spensireli/advanced-cdk-constructs.git
cd advanced-cdk-constructs
```

1. Install dependencies:

```bash
npm install
```

1. Build the project:

```bash
npm run build
```

### Testing

Run the test suite:

```bash
npm test
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For issues and questions, please open an issue on the [GitHub repository](https://github.com/spensireli/advanced-cdk-constructs).
'''
from pkgutil import extend_path
__path__ = extend_path(__path__, __name__)

import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

import typeguard
from importlib.metadata import version as _metadata_package_version
TYPEGUARD_MAJOR_VERSION = int(_metadata_package_version('typeguard').split('.')[0])

def check_type(argname: str, value: object, expected_type: typing.Any) -> typing.Any:
    if TYPEGUARD_MAJOR_VERSION <= 2:
        return typeguard.check_type(argname=argname, value=value, expected_type=expected_type) # type:ignore
    else:
        if isinstance(value, jsii._reference_map.InterfaceDynamicProxy): # pyright: ignore [reportAttributeAccessIssue]
           pass
        else:
            if TYPEGUARD_MAJOR_VERSION == 3:
                typeguard.config.collection_check_strategy = typeguard.CollectionCheckStrategy.ALL_ITEMS # type:ignore
                typeguard.check_type(value=value, expected_type=expected_type) # type:ignore
            else:
                typeguard.check_type(value=value, expected_type=expected_type, collection_check_strategy=typeguard.CollectionCheckStrategy.ALL_ITEMS) # type:ignore

from ._jsii import *

import constructs as _constructs_77d1e7e8


class GuardDutyConstruct(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="advanced-cdk-constructs.GuardDutyConstruct",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        enable_guard_duty: typing.Optional[builtins.bool] = None,
        kubernetes_audit_logs: typing.Optional[builtins.bool] = None,
        malware_protection: typing.Optional[builtins.bool] = None,
        s3_logs: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param enable_guard_duty: 
        :param kubernetes_audit_logs: 
        :param malware_protection: 
        :param s3_logs: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__46f7299fb161d609b36f03ba2aca6e091908d9fb14d778953bdc7011622702eb)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = GuardDutyConstructProps(
            enable_guard_duty=enable_guard_duty,
            kubernetes_audit_logs=kubernetes_audit_logs,
            malware_protection=malware_protection,
            s3_logs=s3_logs,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="detectorId")
    def detector_id(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "detectorId"))

    @detector_id.setter
    def detector_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ac61776a34cb8e70080be2b8c4962494e39c9264a1ce0012d03a34392a271a0d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "detectorId", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="advanced-cdk-constructs.GuardDutyConstructProps",
    jsii_struct_bases=[],
    name_mapping={
        "enable_guard_duty": "enableGuardDuty",
        "kubernetes_audit_logs": "kubernetesAuditLogs",
        "malware_protection": "malwareProtection",
        "s3_logs": "s3Logs",
    },
)
class GuardDutyConstructProps:
    def __init__(
        self,
        *,
        enable_guard_duty: typing.Optional[builtins.bool] = None,
        kubernetes_audit_logs: typing.Optional[builtins.bool] = None,
        malware_protection: typing.Optional[builtins.bool] = None,
        s3_logs: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param enable_guard_duty: 
        :param kubernetes_audit_logs: 
        :param malware_protection: 
        :param s3_logs: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__baf89c1357f24b0c602b710cda32441bac689e805673c53a2cd9ceb645e155bc)
            check_type(argname="argument enable_guard_duty", value=enable_guard_duty, expected_type=type_hints["enable_guard_duty"])
            check_type(argname="argument kubernetes_audit_logs", value=kubernetes_audit_logs, expected_type=type_hints["kubernetes_audit_logs"])
            check_type(argname="argument malware_protection", value=malware_protection, expected_type=type_hints["malware_protection"])
            check_type(argname="argument s3_logs", value=s3_logs, expected_type=type_hints["s3_logs"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if enable_guard_duty is not None:
            self._values["enable_guard_duty"] = enable_guard_duty
        if kubernetes_audit_logs is not None:
            self._values["kubernetes_audit_logs"] = kubernetes_audit_logs
        if malware_protection is not None:
            self._values["malware_protection"] = malware_protection
        if s3_logs is not None:
            self._values["s3_logs"] = s3_logs

    @builtins.property
    def enable_guard_duty(self) -> typing.Optional[builtins.bool]:
        '''
        :stability: experimental
        '''
        result = self._values.get("enable_guard_duty")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def kubernetes_audit_logs(self) -> typing.Optional[builtins.bool]:
        '''
        :stability: experimental
        '''
        result = self._values.get("kubernetes_audit_logs")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def malware_protection(self) -> typing.Optional[builtins.bool]:
        '''
        :stability: experimental
        '''
        result = self._values.get("malware_protection")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def s3_logs(self) -> typing.Optional[builtins.bool]:
        '''
        :stability: experimental
        '''
        result = self._values.get("s3_logs")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GuardDutyConstructProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "GuardDutyConstruct",
    "GuardDutyConstructProps",
]

publication.publish()

def _typecheckingstub__46f7299fb161d609b36f03ba2aca6e091908d9fb14d778953bdc7011622702eb(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    enable_guard_duty: typing.Optional[builtins.bool] = None,
    kubernetes_audit_logs: typing.Optional[builtins.bool] = None,
    malware_protection: typing.Optional[builtins.bool] = None,
    s3_logs: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ac61776a34cb8e70080be2b8c4962494e39c9264a1ce0012d03a34392a271a0d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__baf89c1357f24b0c602b710cda32441bac689e805673c53a2cd9ceb645e155bc(
    *,
    enable_guard_duty: typing.Optional[builtins.bool] = None,
    kubernetes_audit_logs: typing.Optional[builtins.bool] = None,
    malware_protection: typing.Optional[builtins.bool] = None,
    s3_logs: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass
