"""The pods that serve traffic run the image that CI built, scanned and pushed."""


def test_every_pod_runs_the_deployed_digest(app_pods, settings):
    # Arrange: the digest the image ID of each container must end with
    expected = f"@{settings.digest}"

    # Act
    image_ids = [
        status["imageID"]
        for pod in app_pods
        for status in pod["status"]["containerStatuses"]
    ]

    # Assert
    assert image_ids
    assert all(image_id.endswith(expected) for image_id in image_ids), image_ids


def test_every_pod_is_ready_without_restarts(app_pods):
    # Arrange: nothing beyond the app_pods fixture

    # Act
    containers = [
        (pod["metadata"]["name"], status)
        for pod in app_pods
        for status in pod["status"]["containerStatuses"]
    ]

    # Assert
    not_ready = [name for name, status in containers if not status["ready"]]
    restarted = [name for name, status in containers if status["restartCount"] > 0]
    assert not not_ready, f"not ready: {not_ready}"
    assert not restarted, f"restarted: {restarted}"
