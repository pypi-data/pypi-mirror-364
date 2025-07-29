# Platform resources

## How to use

### Feature flag

- We use [unleash](https://www.getunleash.io/) for managing feature flags.
- To toggle the features for now, you have to port-forward the unleash service to your local machine.
- To port-forward the service, run the following command:

  ```bash
  kubectl port-forward -n platform svc/unleash 4242:4242
  ```

#### Feature flag configuration
