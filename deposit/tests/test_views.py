import io
import pytest

from django.urls import reverse

import deposit.views

from deposit.views import get_all_repositories_and_protocols

class TestDepositView():
    """
    Class to group tests for deposit views
    """
    def test_get_all_repositories_and_protocols(self, repository, book_god_of_the_labyrinth, user_isaac_newton):
        """
        Shall return enabled repositories only.
        """
        for i in range(1,3):
            repository.dummy_repository()
        for i in range(1,3):
            repo = repository.dummy_repository()
            repo.enabled=False
            repo.save()

        result = get_all_repositories_and_protocols(book_god_of_the_labyrinth, user_isaac_newton)
        for r in result:
            assert r[0].enabled == True


@pytest.mark.usefixtures('deposit_record')
class TestLetterDeclarationView():
    """
    Tests groups various tests about the LetterDeclarationView
    """

    def test_deposit_record_not_found(self, db, check_status):
        """
        If no deposit record is found, 404
        """
        self.dr.delete()
        check_status(404, 'letter-of-declaration', args=[1])


    @pytest.mark.parametrize('letter_declaration, status', [('', 'pending'), ('test_pdf_generator', 'published'), ('', 'published')])
    def test_letter_not_found(self, check_status, letter_declaration, status):
        """
        A deposit record is found, but conditionds for generating one are not satisfied
        """
        self.dr.repository.letter_declaration = letter_declaration
        self.dr.repository.save()

        self.dr.status = status
        self.dr.save()

        check_status(404, 'letter-of-declaration', args=[self.dr.pk])


    def test_letter_returned(self, monkeypatch, blank_pdf):
        """
        If deposit record is found, user correct, repository requires letter and deposit is pending, return a pdf.
        We mock here the function to generate the pdf.
        """
        monkeypatch.setattr(deposit.views, 'get_declaration_pdf', lambda *args, **kwargs: io.BytesIO(blank_pdf))
        response = self.client.get(reverse('letter-of-declaration', args=[self.dr.pk]))

        assert response.status_code == 200
        assert response.as_attachment == True
        assert response.filename == "Erklärung {}.pdf".format(self.dr.paper.title)
        assert response._headers['content-type'][0] == "Content-Type"
        assert response._headers['content-type'][1] == "application/pdf"

    def test_login_required(self, check_status):
        """
        If the user is not logged in, expect redirect
        """
        self.client.logout()
        check_status(302, 'letter-of-declaration', args=[1])


    def test_wrong_user(self, db, check_status, user_leibniz):
        self.dr.user = user_leibniz
        self.dr.save()
        check_status(403, 'letter-of-declaration', args=[self.dr.pk])
